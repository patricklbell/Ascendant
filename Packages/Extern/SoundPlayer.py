# Based on
# https://github.com/steveway/papagayo-ng/blob/working_vol/SoundPlayer.py

import audioop, os, platform, traceback, wave, pyaudio, threading, copy

from Packages import Settings
from pydub import AudioSegment
from pydub.utils import make_chunks
    
class SoundPlayer:
    """ """
    def __init__(self, soundfile=None):
        self.soundfile = soundfile
        self.isplaying = False
        self.time = 0  # current audio position in frames
        self.audio = pyaudio.PyAudio()
        self.pydubfile = None
        self.volume = 100
        self.reset = False
        self.fade = 0
        self.thread = None

        if not soundfile == None:
            try:
                if Settings.DEBUG:
                    print(self.soundfile)
                self.pydubfile = AudioSegment.from_file(self.soundfile, format=os.path.splitext(self.soundfile)[1][1:])

                self.isvalid = True

            except:
                traceback.print_exc()
                self.wave_reference = None
                self.isvalid = False
        else:
            self.isvalid = False

    def IsValid(self):
        """ """
        return self.isvalid

    def Duration(self):
        """ """
        return(self.pydubfile.duration_seconds)

    def GetRMSAmplitude(self, time, sampleDur):
        """

        :param time: 
        :param sampleDur: 

        """
        return self.pydubfile[time*1000.0:(time+sampleDur)*1000.0].rms
        
    def IsPlaying(self):
        """ """
        if not self.thread == None:
            return self.thread.is_alive()
        return False

    def SetCurTime(self, time):
        """

        :param time: 

        """
        self.time = time

    def Stop(self, fade_out_ms:int=0):
        """

        :param fade_out_ms:int:  (Default value = 0)

        """
        if not fade_out_ms == 0:
            self.fade = -fade_out_ms
        self.isplaying = False

    def CurrentTime(self):
        """ """
        return self.time

    def SetVolume(self, volume):
        """

        :param volume: 

        """
        self.volume = volume
        if self.isplaying:
            p_time = self.time
            self.Stop()
            self.PlaySegment(p_time, self.pydubfile.duration_seconds-p_time)

    def _play(self, start, length, loops):
        """

        :param start: 
        :param length: 
        :param loops: 

        """
        self.isplaying = True

        millisecondchunk = 50 / 1000.0

        stream = self.audio.open(format=
                                    self.audio.get_format_from_width(self.pydubfile.sample_width),
                                    channels=self.pydubfile.channels,
                                    rate=self.pydubfile.frame_rate,
                                    output=True)

        if self.volume == 0:
            playchunk = AudioSegment.silent(duration=length*1000)
        else:
            playchunk = self.pydubfile[start*1000.0:(start+length)*1000.0] - (60 - (60 * (self.volume/100.0)))

        if self.fade > 0:
            playchunk = playchunk.fade_in(self.fade)

        self.time = start
        for chunks in make_chunks(playchunk, millisecondchunk*1000):
            self.time += millisecondchunk
            stream.write(chunks._data)
            if not self.isplaying:
                # Fade out
                if self.fade < 0:
                    playchunk = (self.pydubfile[self.time*1000:self.time*1000 - self.fade] - (60 - (60 * (self.volume/100.0)))).fade_out(-self.fade)
                    for chunks in make_chunks(playchunk, millisecondchunk*1000):
                        self.time += millisecondchunk
                        stream.write(chunks._data)

                stream.close()
                self.isplaying = False
                return
            if self.time >= start+length:
                break
            if self.reset:
                self.reset = False
                self._play(0, length, loops)

        
        if not loops == 1:
            if loops == -1:
                self._play(0, length, -1)
            else:
                self._play(0, length, loops-1)
        else:
            stream.close()
            self.isplaying = False

    def Play(self, loops=1, fade_in_ms=0):
        """

        :param loops:  (Default value = 1)
        :param fade_in_ms:  (Default value = 0)

        """
        if not fade_in_ms == 0:
            self.fade = fade_in_ms
        if self.isplaying:
            self.reset = True
        else:
            if not self.thread == None:
                self.Stop()
                self.thread.join()
            
            self.thread = threading.Thread(daemon=True, target=self._play, args=(0, self.Duration(), loops))
            self.thread.start()

    def PlaySegment(self, start, length):
        """

        :param start: 
        :param length: 

        """
        if not self.isplaying:  # otherwise this get's kinda echo-y
            if not self.thread == None:
                self.Stop()
                self.thread.join()
            
            self.thread = threading.Thread(daemon=True, target=self._play, args=(start, length, 1))
            self.thread.start()
    

    # Define custom unpickle methods
    def __setstate__(self, d):
        self.__init__()
        self.pydubfile = d["pydubfile"]
        self.volume = d["volume"]
        self.soundfile = d["soundfile"]
        self.isvalid = True
    
    def __getstate__(self):
        if not self.thread == None:
            self.Stop()
            self.thread.join()
        return {"soundfile":self.soundfile,"volume":self.volume, "pydubfile":self.pydubfile}