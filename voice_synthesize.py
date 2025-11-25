from music8bit import *
from music8bit import WaveGenerator
from music8bit.utils import _validate
from .pico_formants import formants
import numpy as np
from scipy.signal import square,butter,sosfilt

def bpf(wave,formant):
  """bpfフィルタ関数"""
  filtered = np.zeros_like(wave)
  for fc, bw in formant:
      low = fc - bw / 2
      high = fc + bw / 2
      sos = butter(2, [low, high], btype='band', fs=22050, output='sos')
      filtered += sosfilt(sos, wave)
  return filtered

def apply_fade(wave, fade_time):
    """音の前後にフェードをかけて自然に音を変更するための関数"""
    wave = np.atleast_1d(wave)
    fade_samples = int(22050 * fade_time)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)

    if len(wave) > 2 * fade_samples:
        wave[:fade_samples] *= fade_in
        wave[-fade_samples:] *= fade_out
    return wave

class SyntheticVoice(WaveGenerator):
    """フォルマントにしたがって合成音声を作る部分"""
    @property
    def using_others(self):
        return True

    def __init__(self,vibrato=False):
        self.vibrato = int(vibrato)

    def generate(self, freq, t, vowel:list):
        formant = formants[vowel[0]]
        mod = np.sin(2*np.pi*5*t) * int(self.vibrato) # ビブラート選択
        base_pulse =  square(2 * np.pi * freq * t,duty=0.25) # 基本振動(dutyは12.5%)
        return np.array([apply_fade(bpf(base_pulse,formant),0.08)])
