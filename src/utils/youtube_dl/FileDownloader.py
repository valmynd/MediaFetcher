#!/usr/bin/env python
# -*- coding: utf-8 -*-



import math
import io
import os
import re
import socket
import subprocess
import sys
import time
import traceback

if os.name == 'nt':
    import ctypes

from .utils import *


class FileDownloader(object):
    """File Downloader class.

    File downloader objects are the ones responsible of downloading the
    actual video file and writing it to disk if the user has requested
    it, among some other tasks. In most cases there should be one per
    program. As, given a video URL, the downloader doesn't know how to
    extract all the needed information, task that InfoExtractors do, it
    has to pass the URL to one of them.

    For this, file downloader objects have a method that allows
    InfoExtractors to be registered in a given order. When it is passed
    a URL, the file downloader handles it to the first InfoExtractor it
    finds that reports being able to handle it. The InfoExtractor extracts
    all the information about the video or videos the URL refers to, and
    asks the FileDownloader to process the video information, possibly
    downloading the video.

    File downloaders accept a lot of parameters. In order not to saturate
    the object constructor with arguments, it receives a dictionary of
    options instead. These options are available through the params
    attribute for the InfoExtractors to use. The FileDownloader also
    registers itself as the downloader in charge for the InfoExtractors
    that are added to it, so this is a "mutual registration".

    Available options:

    username:          Username for authentication purposes.
    password:          Password for authentication purposes.
    usenetrc:          Use netrc for authentication instead.
    quiet:             Do not print messages to stdout.
    forceurl:          Force printing final URL.
    forcetitle:        Force printing title.
    forcethumbnail:    Force printing thumbnail URL.
    forcedescription:  Force printing description.
    forcefilename:     Force printing final filename.
    simulate:          Do not download the video files.
    format:            Video format code.
    format_limit:      Highest quality format to try.
    outtmpl:           Template for output names.
    restrictfilenames: Do not allow "&" and spaces in file names
    ignoreerrors:      Do not stop on download errors.
    ratelimit:         Download speed limit, in bytes/sec.
    nooverwrites:      Prevent overwriting files.
    retries:           Number of times to retry for HTTP error 5xx
    buffersize:        Size of download buffer in bytes.
    noresizebuffer:    Do not automatically resize the download buffer.
    continuedl:        Try to continue downloads if possible.
    noprogress:        Do not print the progress bar.
    playliststart:     Playlist item to start at.
    playlistend:       Playlist item to end at.
    matchtitle:        Download only matching titles.
    rejecttitle:       Reject downloads for matching titles.
    logtostderr:       Log messages to stderr instead of stdout.
    consoletitle:      Display progress in console window's titlebar.
    nopart:            Do not use temporary .part files.
    updatetime:        Use the Last-modified header to set output file timestamps.
    writedescription:  Write the video description to a .description file
    writeinfojson:     Write the video description to a .info.json file
    writesubtitles:    Write the video subtitles to a file
    onlysubtitles:     Downloads only the subtitles of the video
    allsubtitles:      Downloads all the subtitles of the video
    listsubtitles:     Lists all available subtitles for the video
    subtitlesformat:   Subtitle format [sbv/srt] (default=srt)
    subtitleslang:     Language of the subtitles to download
    test:              Download only first bytes to test the downloader.
    keepvideo:         Keep the video file after post-processing
    min_filesize:      Skip files smaller than this size
    max_filesize:      Skip files larger than this size
    """

    params = None
    _ies = []
    _pps = []
    _download_retcode = None
    _num_downloads = None
    _screen_file = None

    def __init__(self, params):
        """Create a FileDownloader object with the given options."""
        self._ies = []
        self._pps = []
        self._progress_hooks = []
        self._download_retcode = 0
        self._num_downloads = 0
        self._screen_file = [sys.stdout, sys.stderr][params.get('logtostderr', False)]
        self.params = params

        if '%(stitle)s' in self.params['outtmpl']:
            self.report_warning('%(stitle)s is deprecated. Use the %(title)s and the --restrict-filenames flag(which also secures %(uploader)s et al) instead.')

    @staticmethod
    def format_bytes(bytes):
        if bytes is None:
            return 'N/A'
        if type(bytes) is str:
            bytes = float(bytes)
        if bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(bytes, 1024.0))
        suffix = 'bkMGTPEZY'[exponent]
        converted = float(bytes) / float(1024 ** exponent)
        return '%.2f%s' % (converted, suffix)

    @staticmethod
    def calc_percent(byte_counter, data_len):
        if data_len is None:
            return '---.-%'
        return '%6s' % ('%3.1f%%' % (float(byte_counter) / float(data_len) * 100.0))

    @staticmethod
    def calc_eta(start, now, total, current):
        if total is None:
            return '--:--'
        dif = now - start
        if current == 0 or dif < 0.001: # One millisecond
            return '--:--'
        rate = float(current) / dif
        eta = int((float(total) - float(current)) / rate)
        (eta_mins, eta_secs) = divmod(eta, 60)
        if eta_mins > 99:
            return '--:--'
        return '%02d:%02d' % (eta_mins, eta_secs)

    @staticmethod
    def calc_speed(start, now, bytes):
        dif = now - start
        if bytes == 0 or dif < 0.001: # One millisecond
            return '%10s' % '---b/s'
        return '%10s' % ('%s/s' % FileDownloader.format_bytes(float(bytes) / dif))

    @staticmethod
    def best_block_size(elapsed_time, bytes):
        new_min = max(bytes / 2.0, 1.0)
        new_max = min(max(bytes * 2.0, 1.0), 4194304) # Do not surpass 4 MB
        if elapsed_time < 0.001:
            return int(new_max)
        rate = bytes / elapsed_time
        if rate > new_max:
            return int(new_max)
        if rate < new_min:
            return int(new_min)
        return int(rate)

    @staticmethod
    def parse_bytes(bytestr):
        """Parse a string indicating a byte quantity into an integer."""
        matchobj = re.match(r'(?i)^(\d+(?:\.\d+)?)([kMGTPEZY]?)$', bytestr)
        if matchobj is None:
            return None
        number = float(matchobj.group(1))
        multiplier = 1024.0 ** 'bkmgtpezy'.index(matchobj.group(2).lower())
        return int(round(number * multiplier))

    def add_info_extractor(self, ie):
        """Add an InfoExtractor object to the end of the list."""
        self._ies.append(ie)
        ie.set_downloader(self)

    def add_post_processor(self, pp):
        """Add a PostProcessor object to the end of the chain."""
        self._pps.append(pp)
        pp.set_downloader(self)

    def to_screen(self, message, skip_eol=False):
        """Print message to stdout if not in quiet mode."""
        assert type(message) == type('')
        if not self.params.get('quiet', False):
            terminator = ['\n', ''][skip_eol]
            output = message + terminator
            if 'b' in getattr(self._screen_file, 'mode', '') or sys.version_info[0] < 3: # Python 2 lies about the mode of sys.stdout/sys.stderr
                output = output.encode(preferredencoding(), 'ignore')
            self._screen_file.write(output)
            self._screen_file.flush()

    def to_stderr(self, message):
        """Print message to stderr."""
        assert type(message) == type('')
        output = message + '\n'
        if 'b' in getattr(self._screen_file, 'mode', '') or sys.version_info[0] < 3: # Python 2 lies about the mode of sys.stdout/sys.stderr
            output = output.encode(preferredencoding())
        sys.stderr.write(output)

    def to_cons_title(self, message):
        """Set console/terminal window title to message."""
        if not self.params.get('consoletitle', False):
            return
        if os.name == 'nt' and ctypes.windll.kernel32.GetConsoleWindow():
            # c_wchar_p() might not be necessary if `message` is
            # already of type unicode()
            ctypes.windll.kernel32.SetConsoleTitleW(ctypes.c_wchar_p(message))
        elif 'TERM' in os.environ:
            self.to_screen('\033]0;%s\007' % message, skip_eol=True)

    def fixed_template(self):
        """Checks if the output template is fixed."""
        return (re.search('(?u)%\\(.+?\\)s', self.params['outtmpl']) is None)

    def trouble(self, message=None, tb=None):
        """Determine action to take when a download problem appears.

        Depending on if the downloader has been configured to ignore
        download errors or not, this method may throw an exception or
        not when errors are found, after printing the message.

        tb, if given, is additional traceback information.
        """
        if message is not None:
            self.to_stderr(message)
        if self.params.get('verbose'):
            if tb is None:
                if sys.exc_info()[0]:  # if .trouble has been called from an except block
                    tb = ''
                    if hasattr(sys.exc_info()[1], 'exc_info') and sys.exc_info()[1].exc_info[0]:
                        tb += ''.join(traceback.format_exception(*sys.exc_info()[1].exc_info))
                    tb += compat_str(traceback.format_exc())
                else:
                    tb_data = traceback.format_list(traceback.extract_stack())
                    tb = ''.join(tb_data)
            self.to_stderr(tb)
        if not self.params.get('ignoreerrors', False):
            if sys.exc_info()[0] and hasattr(sys.exc_info()[1], 'exc_info') and sys.exc_info()[1].exc_info[0]:
                exc_info = sys.exc_info()[1].exc_info
            else:
                exc_info = sys.exc_info()
            raise DownloadError(message, exc_info)
        self._download_retcode = 1

    def report_warning(self, message):
        '''
        Print the message to stderr, it will be prefixed with 'WARNING:'
        If stderr is a tty file the 'WARNING:' will be colored
        '''
        if sys.stderr.isatty():
            _msg_header='\033[0;33mWARNING:\033[0m'
        else:
            _msg_header='WARNING:'
        warning_message='%s %s' % (_msg_header,message)
        self.to_stderr(warning_message)

    def report_error(self, message, tb=None):
        '''
        Do the same as trouble, but prefixes the message with 'ERROR:', colored
        in red if stderr is a tty file.
        '''
        if sys.stderr.isatty():
            _msg_header = '\033[0;31mERROR:\033[0m'
        else:
            _msg_header = 'ERROR:'
        error_message = '%s %s' % (_msg_header, message)
        self.trouble(error_message, tb)

    def slow_down(self, start_time, byte_counter):
        """Sleep if the download speed is over the rate limit."""
        rate_limit = self.params.get('ratelimit', None)
        if rate_limit is None or byte_counter == 0:
            return
        now = time.time()
        elapsed = now - start_time
        if elapsed <= 0.0:
            return
        speed = float(byte_counter) / elapsed
        if speed > rate_limit:
            time.sleep((byte_counter - rate_limit * (now - start_time)) / rate_limit)

    def temp_name(self, filename):
        """Returns a temporary filename for the given filename."""
        if self.params.get('nopart', False) or filename == '-' or \
                (os.path.exists(encodeFilename(filename)) and not os.path.isfile(encodeFilename(filename))):
            return filename
        return filename + '.part'

    def undo_temp_name(self, filename):
        if filename.endswith('.part'):
            return filename[:-len('.part')]
        return filename

    def try_rename(self, old_filename, new_filename):
        try:
            if old_filename == new_filename:
                return
            os.rename(encodeFilename(old_filename), encodeFilename(new_filename))
        except (IOError, OSError) as err:
            self.report_error('unable to rename file')

    def try_utime(self, filename, last_modified_hdr):
        """Try to set the last-modified time of the given file."""
        if last_modified_hdr is None:
            return
        if not os.path.isfile(encodeFilename(filename)):
            return
        timestr = last_modified_hdr
        if timestr is None:
            return
        filetime = timeconvert(timestr)
        if filetime is None:
            return filetime
        try:
            os.utime(filename, (time.time(), filetime))
        except:
            pass
        return filetime

    def report_writedescription(self, descfn):
        """ Report that the description file is being written """
        self.to_screen('[info] Writing video description to: ' + descfn)

    def report_writesubtitles(self, sub_filename):
        """ Report that the subtitles file is being written """
        self.to_screen('[info] Writing video subtitles to: ' + sub_filename)

    def report_writeinfojson(self, infofn):
        """ Report that the metadata file has been written """
        self.to_screen('[info] Video description metadata as JSON to: ' + infofn)

    def report_destination(self, filename):
        """Report destination filename."""
        self.to_screen('[download] Destination: ' + filename)

    def report_progress(self, percent_str, data_len_str, speed_str, eta_str):
        """Report download progress."""
        if self.params.get('noprogress', False):
            return
        if self.params.get('progress_with_newline', False):
            self.to_screen('[download] %s of %s at %s ETA %s' %
                (percent_str, data_len_str, speed_str, eta_str))
        else:
            self.to_screen('\r[download] %s of %s at %s ETA %s' %
                (percent_str, data_len_str, speed_str, eta_str), skip_eol=True)
        self.to_cons_title('youtube-dl - %s of %s at %s ETA %s' %
                (percent_str.strip(), data_len_str.strip(), speed_str.strip(), eta_str.strip()))

    def report_resuming_byte(self, resume_len):
        """Report attempt to resume at given byte."""
        self.to_screen('[download] Resuming download at byte %s' % resume_len)

    def report_retry(self, count, retries):
        """Report retry in case of HTTP error 5xx"""
        self.to_screen('[download] Got server HTTP error. Retrying (attempt %d of %d)...' % (count, retries))

    def report_file_already_downloaded(self, file_name):
        """Report file has already been fully downloaded."""
        try:
            self.to_screen('[download] %s has already been downloaded' % file_name)
        except (UnicodeEncodeError) as err:
            self.to_screen('[download] The file has already been downloaded')

    def report_unable_to_resume(self):
        """Report it was impossible to resume download."""
        self.to_screen('[download] Unable to resume')

    def report_finish(self):
        """Report download finished."""
        if self.params.get('noprogress', False):
            self.to_screen('[download] Download completed')
        else:
            self.to_screen('')

    def increment_downloads(self):
        """Increment the ordinal that assigns a number to each file."""
        self._num_downloads += 1

    def prepare_filename(self, info_dict):
        """Generate the output filename."""
        try:
            template_dict = dict(info_dict)

            template_dict['epoch'] = int(time.time())
            autonumber_size = self.params.get('autonumber_size')
            if autonumber_size is None:
                autonumber_size = 5
            autonumber_templ = '%0' + str(autonumber_size) + 'd'
            template_dict['autonumber'] = autonumber_templ % self._num_downloads

            sanitize = lambda k,v: sanitize_filename(
                'NA' if v is None else compat_str(v),
                restricted=self.params.get('restrictfilenames'),
                is_id=(k=='id'))
            template_dict = dict((k, sanitize(k, v)) for k,v in list(template_dict.items()))

            filename = self.params['outtmpl'] % template_dict
            return filename
        except KeyError as err:
            self.trouble('ERROR: Erroneous output template')
            return None
        except ValueError as err:
            self.trouble('ERROR: Insufficient system charset ' + repr(preferredencoding()))
            return None

    def _match_entry(self, info_dict):
        """ Returns None iff the file should be downloaded """

        title = info_dict['title']
        matchtitle = self.params.get('matchtitle', False)
        if matchtitle:
            if not re.search(matchtitle, title, re.IGNORECASE):
                return '[download] "' + title + '" title did not match pattern "' + matchtitle + '"'
        rejecttitle = self.params.get('rejecttitle', False)
        if rejecttitle:
            if re.search(rejecttitle, title, re.IGNORECASE):
                return '"' + title + '" title matched reject pattern "' + rejecttitle + '"'
        return None

    def process_info(self, info_dict):
        """Process a single dictionary returned by an InfoExtractor."""

        # Keep for backwards compatibility
        info_dict['stitle'] = info_dict['title']

        if not 'format' in info_dict:
            info_dict['format'] = info_dict['ext']

        reason = self._match_entry(info_dict)
        if reason is not None:
            self.to_screen('[download] ' + reason)
            return

        max_downloads = self.params.get('max_downloads')
        if max_downloads is not None:
            if self._num_downloads > int(max_downloads):
                raise MaxDownloadsReached()

        filename = self.prepare_filename(info_dict)

        # Forced printings
        if self.params.get('forcetitle', False):
            compat_print(info_dict['title'])
        if self.params.get('forceurl', False):
            compat_print(info_dict['url'])
        if self.params.get('forcethumbnail', False) and 'thumbnail' in info_dict:
            compat_print(info_dict['thumbnail'])
        if self.params.get('forcedescription', False) and 'description' in info_dict:
            compat_print(info_dict['description'])
        if self.params.get('forcefilename', False) and filename is not None:
            compat_print(filename)
        if self.params.get('forceformat', False):
            compat_print(info_dict['format'])

        # Do nothing else if in simulate mode
        if self.params.get('simulate', False):
            return

        if filename is None:
            return

        try:
            dn = os.path.dirname(encodeFilename(filename))
            if dn != '' and not os.path.exists(dn): # dn is already encoded
                os.makedirs(dn)
        except (OSError, IOError) as err:
            self.report_error('unable to create directory ' + compat_str(err))
            return

        if self.params.get('writedescription', False):
            try:
                descfn = filename + '.description'
                self.report_writedescription(descfn)
                with io.open(encodeFilename(descfn), 'w', encoding='utf-8') as descfile:
                    descfile.write(info_dict['description'])
            except (OSError, IOError):
                self.report_error('Cannot write description file ' + descfn)
                return

        if self.params.get('writesubtitles', False) and 'subtitles' in info_dict and info_dict['subtitles']:
            # subtitles download errors are already managed as troubles in relevant IE
            # that way it will silently go on when used with unsupporting IE
            subtitle = info_dict['subtitles'][0]
            (sub_error, sub_lang, sub) = subtitle
            sub_format = self.params.get('subtitlesformat')
            if sub_error:
                self.report_warning("Some error while getting the subtitles")
            else:
                try:
                    sub_filename = filename.rsplit('.', 1)[0] + '.' + sub_lang + '.' + sub_format
                    self.report_writesubtitles(sub_filename)
                    with io.open(encodeFilename(sub_filename), 'w', encoding='utf-8') as subfile:
                        subfile.write(sub)
                except (OSError, IOError):
                    self.report_error('Cannot write subtitles file ' + descfn)
                    return
            if self.params.get('onlysubtitles', False):
                return 

        if self.params.get('allsubtitles', False) and 'subtitles' in info_dict and info_dict['subtitles']:
            subtitles = info_dict['subtitles']
            sub_format = self.params.get('subtitlesformat')
            for subtitle in subtitles:
                (sub_error, sub_lang, sub) = subtitle
                if sub_error:
                    self.report_warning("Some error while getting the subtitles")
                else:
                    try:
                        sub_filename = filename.rsplit('.', 1)[0] + '.' + sub_lang + '.' + sub_format
                        self.report_writesubtitles(sub_filename)
                        with io.open(encodeFilename(sub_filename), 'w', encoding='utf-8') as subfile:
                                subfile.write(sub)
                    except (OSError, IOError):
                        self.trouble('ERROR: Cannot write subtitles file ' + descfn)
                        return
            if self.params.get('onlysubtitles', False):
                return 

        if self.params.get('writeinfojson', False):
            infofn = filename + '.info.json'
            self.report_writeinfojson(infofn)
            try:
                json_info_dict = dict((k, v) for k,v in list(info_dict.items()) if not k in ['urlhandle'])
                write_json_file(json_info_dict, encodeFilename(infofn))
            except (OSError, IOError):
                self.report_error('Cannot write metadata to JSON file ' + infofn)
                return

        if not self.params.get('skip_download', False):
            if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(filename)):
                success = True
            else:
                try:
                    success = self._do_download(filename, info_dict)
                except (OSError, IOError) as err:
                    raise UnavailableVideoError()
                except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
                    self.report_error('unable to download video data: %s' % str(err))
                    return
                except (ContentTooShortError, ) as err:
                    self.report_error('content too short (expected %s bytes and served %s)' % (err.expected, err.downloaded))
                    return

            if success:
                try:
                    self.post_process(filename, info_dict)
                except (PostProcessingError) as err:
                    self.report_error('postprocessing: %s' % str(err))
                    return

    def download(self, url_list):
        """Download a given list of URLs."""
        if len(url_list) > 1 and self.fixed_template():
            raise SameFileError(self.params['outtmpl'])

        for url in url_list:
            suitable_found = False
            for ie in self._ies:
                # Go to next InfoExtractor if not suitable
                if not ie.suitable(url):
                    continue

                # Warn if the _WORKING attribute is False
                if not ie.working():
                    self.report_warning('the program functionality for this site has been marked as broken, '
                                        'and will probably not work. If you want to go on, use the -i option.')

                # Suitable InfoExtractor found
                suitable_found = True

                # Extract information from URL and process it
                try:
                    videos = ie.extract(url)
                except ExtractorError as de: # An error we somewhat expected
                    self.trouble('ERROR: ' + compat_str(de), de.format_traceback())
                    break
                except MaxDownloadsReached:
                    self.to_screen('[info] Maximum number of downloaded files reached.')
                    raise
                except Exception as e:
                    if self.params.get('ignoreerrors', False):
                        self.report_error('' + compat_str(e), tb=compat_str(traceback.format_exc()))
                        break
                    else:
                        raise

                if len(videos or []) > 1 and self.fixed_template():
                    raise SameFileError(self.params['outtmpl'])

                for video in videos or []:
                    video['extractor'] = ie.IE_NAME
                    try:
                        self.increment_downloads()
                        self.process_info(video)
                    except UnavailableVideoError:
                        self.to_stderr("\n")
                        self.report_error('unable to download video')

                # Suitable InfoExtractor had been found; go to next URL
                break

            if not suitable_found:
                self.report_error('no suitable InfoExtractor: %s' % url)

        return self._download_retcode

    def post_process(self, filename, ie_info):
        """Run all the postprocessors on the given file."""
        info = dict(ie_info)
        info['filepath'] = filename
        keep_video = None
        for pp in self._pps:
            try:
                keep_video_wish,new_info = pp.run(info)
                if keep_video_wish is not None:
                    if keep_video_wish:
                        keep_video = keep_video_wish
                    elif keep_video is None:
                        # No clear decision yet, let IE decide
                        keep_video = keep_video_wish
            except PostProcessingError as e:
                self.to_stderr('ERROR: ' + e.msg)
        if keep_video is False and not self.params.get('keepvideo', False):
            try:
                self.to_screen('Deleting original file %s (pass -k to keep)' % filename)
                os.remove(encodeFilename(filename))
            except (IOError, OSError):
                self.report_warning('Unable to remove downloaded video file')

    def _download_with_rtmpdump(self, filename, url, player_url, page_url, play_path):
        self.report_destination(filename)
        tmpfilename = self.temp_name(filename)

        # Check for rtmpdump first
        try:
            subprocess.call(['rtmpdump', '-h'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
        except (OSError, IOError):
            self.report_error('RTMP download detected but "rtmpdump" could not be run')
            return False

        # Download using rtmpdump. rtmpdump returns exit code 2 when
        # the connection was interrumpted and resuming appears to be
        # possible. This is part of rtmpdump's normal usage, AFAIK.
        basic_args = ['rtmpdump', '-q', '-r', url, '-o', tmpfilename]
        if player_url is not None:
            basic_args += ['-W', player_url]
        if page_url is not None:
            basic_args += ['--pageUrl', page_url]
        if play_path is not None:
            basic_args += ['-y', play_path]
        args = basic_args + [[], ['-e', '-k', '1']][self.params.get('continuedl', False)]
        if self.params.get('verbose', False):
            try:
                import pipes
                shell_quote = lambda args: ' '.join(map(pipes.quote, args))
            except ImportError:
                shell_quote = repr
            self.to_screen('[debug] rtmpdump command line: ' + shell_quote(args))
        retval = subprocess.call(args)
        while retval == 2 or retval == 1:
            prevsize = os.path.getsize(encodeFilename(tmpfilename))
            self.to_screen('\r[rtmpdump] %s bytes' % prevsize, skip_eol=True)
            time.sleep(5.0) # This seems to be needed
            retval = subprocess.call(basic_args + ['-e'] + [[], ['-k', '1']][retval == 1])
            cursize = os.path.getsize(encodeFilename(tmpfilename))
            if prevsize == cursize and retval == 1:
                break
             # Some rtmp streams seem abort after ~ 99.8%. Don't complain for those
            if prevsize == cursize and retval == 2 and cursize > 1024:
                self.to_screen('\r[rtmpdump] Could not download the whole video. This can happen for some advertisements.')
                retval = 0
                break
        if retval == 0:
            fsize = os.path.getsize(encodeFilename(tmpfilename))
            self.to_screen('\r[rtmpdump] %s bytes' % fsize)
            self.try_rename(tmpfilename, filename)
            self._hook_progress({
                'downloaded_bytes': fsize,
                'total_bytes': fsize,
                'filename': filename,
                'status': 'finished',
            })
            return True
        else:
            self.to_stderr("\n")
            self.report_error('rtmpdump exited with code %d' % retval)
            return False

    def _do_download(self, filename, info_dict):
        url = info_dict['url']

        # Check file already present
        if self.params.get('continuedl', False) and os.path.isfile(encodeFilename(filename)) and not self.params.get('nopart', False):
            self.report_file_already_downloaded(filename)
            self._hook_progress({
                'filename': filename,
                'status': 'finished',
            })
            return True

        # Attempt to download using rtmpdump
        if url.startswith('rtmp'):
            return self._download_with_rtmpdump(filename, url,
                                                info_dict.get('player_url', None),
                                                info_dict.get('page_url', None),
                                                info_dict.get('play_path', None))

        tmpfilename = self.temp_name(filename)
        stream = None

        # Do not include the Accept-Encoding header
        headers = {'Youtubedl-no-compression': 'True'}
        if 'user_agent' in info_dict:
            headers['Youtubedl-user-agent'] = info_dict['user_agent']
        basic_request = compat_urllib_request.Request(url, None, headers)
        request = compat_urllib_request.Request(url, None, headers)

        if self.params.get('test', False):
            request.add_header('Range','bytes=0-10240')

        # Establish possible resume length
        if os.path.isfile(encodeFilename(tmpfilename)):
            resume_len = os.path.getsize(encodeFilename(tmpfilename))
        else:
            resume_len = 0

        open_mode = 'wb'
        if resume_len != 0:
            if self.params.get('continuedl', False):
                self.report_resuming_byte(resume_len)
                request.add_header('Range','bytes=%d-' % resume_len)
                open_mode = 'ab'
            else:
                resume_len = 0

        count = 0
        retries = self.params.get('retries', 0)
        while count <= retries:
            # Establish connection
            try:
                if count == 0 and 'urlhandle' in info_dict:
                    data = info_dict['urlhandle']
                data = compat_urllib_request.urlopen(request)
                break
            except (compat_urllib_error.HTTPError, ) as err:
                if (err.code < 500 or err.code >= 600) and err.code != 416:
                    # Unexpected HTTP error
                    raise
                elif err.code == 416:
                    # Unable to resume (requested range not satisfiable)
                    try:
                        # Open the connection again without the range header
                        data = compat_urllib_request.urlopen(basic_request)
                        content_length = data.info()['Content-Length']
                    except (compat_urllib_error.HTTPError, ) as err:
                        if err.code < 500 or err.code >= 600:
                            raise
                    else:
                        # Examine the reported length
                        if (content_length is not None and
                                (resume_len - 100 < int(content_length) < resume_len + 100)):
                            # The file had already been fully downloaded.
                            # Explanation to the above condition: in issue #175 it was revealed that
                            # YouTube sometimes adds or removes a few bytes from the end of the file,
                            # changing the file size slightly and causing problems for some users. So
                            # I decided to implement a suggested change and consider the file
                            # completely downloaded if the file size differs less than 100 bytes from
                            # the one in the hard drive.
                            self.report_file_already_downloaded(filename)
                            self.try_rename(tmpfilename, filename)
                            self._hook_progress({
                                'filename': filename,
                                'status': 'finished',
                            })
                            return True
                        else:
                            # The length does not match, we start the download over
                            self.report_unable_to_resume()
                            open_mode = 'wb'
                            break
            # Retry
            count += 1
            if count <= retries:
                self.report_retry(count, retries)

        if count > retries:
            self.report_error('giving up after %s retries' % retries)
            return False

        data_len = data.info().get('Content-length', None)
        if data_len is not None:
            data_len = int(data_len) + resume_len
            min_data_len = self.params.get("min_filesize", None)
            max_data_len =  self.params.get("max_filesize", None)
            if min_data_len is not None and data_len < min_data_len:
                self.to_screen('\r[download] File is smaller than min-filesize (%s bytes < %s bytes). Aborting.' % (data_len, min_data_len))
                return False
            if max_data_len is not None and data_len > max_data_len:
                self.to_screen('\r[download] File is larger than max-filesize (%s bytes > %s bytes). Aborting.' % (data_len, max_data_len))
                return False

        data_len_str = self.format_bytes(data_len)
        byte_counter = 0 + resume_len
        block_size = self.params.get('buffersize', 1024)
        start = time.time()
        while True:
            # Download and write
            before = time.time()
            data_block = data.read(block_size)
            after = time.time()
            if len(data_block) == 0:
                break
            byte_counter += len(data_block)

            # Open file just in time
            if stream is None:
                try:
                    (stream, tmpfilename) = sanitize_open(tmpfilename, open_mode)
                    assert stream is not None
                    filename = self.undo_temp_name(tmpfilename)
                    self.report_destination(filename)
                except (OSError, IOError) as err:
                    self.report_error('unable to open for writing: %s' % str(err))
                    return False
            try:
                stream.write(data_block)
            except (IOError, OSError) as err:
                self.to_stderr("\n")
                self.report_error('unable to write data: %s' % str(err))
                return False
            if not self.params.get('noresizebuffer', False):
                block_size = self.best_block_size(after - before, len(data_block))

            # Progress message
            speed_str = self.calc_speed(start, time.time(), byte_counter - resume_len)
            if data_len is None:
                self.report_progress('Unknown %', data_len_str, speed_str, 'Unknown ETA')
            else:
                percent_str = self.calc_percent(byte_counter, data_len)
                eta_str = self.calc_eta(start, time.time(), data_len - resume_len, byte_counter - resume_len)
                self.report_progress(percent_str, data_len_str, speed_str, eta_str)

            self._hook_progress({
                'downloaded_bytes': byte_counter,
                'total_bytes': data_len,
                'tmpfilename': tmpfilename,
                'filename': filename,
                'status': 'downloading',
            })

            # Apply rate limit
            self.slow_down(start, byte_counter - resume_len)

        if stream is None:
            self.to_stderr("\n")
            self.report_error('Did not get any data blocks')
            return False
        stream.close()
        self.report_finish()
        if data_len is not None and byte_counter != data_len:
            raise ContentTooShortError(byte_counter, int(data_len))
        self.try_rename(tmpfilename, filename)

        # Update file modification time
        if self.params.get('updatetime', True):
            info_dict['filetime'] = self.try_utime(filename, data.info().get('last-modified', None))

        self._hook_progress({
            'downloaded_bytes': byte_counter,
            'total_bytes': byte_counter,
            'filename': filename,
            'status': 'finished',
        })

        return True

    def _hook_progress(self, status):
        for ph in self._progress_hooks:
            ph(status)

    def add_progress_hook(self, ph):
        """ ph gets called on download progress, with a dictionary with the entries
        * filename: The final filename
        * status: One of "downloading" and "finished"

        It can also have some of the following entries:

        * downloaded_bytes: Bytes on disks
        * total_bytes: Total bytes, None if unknown
        * tmpfilename: The filename we're currently writing to

        Hooks are guaranteed to be called at least once (with status "finished")
        if the download is successful.
        """
        self._progress_hooks.append(ph)
