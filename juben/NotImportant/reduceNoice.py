import numpy as np
import scipy.io.wavfile as wf
import numpy.fft as nf


sample_rate,noised_sigs = wf.read("voice.wav")
print("sample_rate",sample_rate)
print("niosed_sigs",noised_sigs.shape)

times = np.arange(len(noised_sigs))/sample_rate      #每一个x值是几秒 最后一个 220500/44100



#傅里叶变换，获得频域信息，画出频谱图
freqs = nf.fftfreq(times.size,1/sample_rate)
complex_ary = nf.fft(noised_sigs)
powers = np.abs(complex_ary)



#删除低能量噪声
fund_freq = freqs[powers.argmax()]
#找下标 所有频率不等于最大频率的
#noised_indices = np.where(freqs!=fund_freq)
noised_indices = np.where(powers<100000000)
#noised_indices = np.where(freqs>1500)
#制作一个副本
complex_filter = complex_ary.copy()
#将副本中，频率不符的
complex_filter[noised_indices] = 0

power_filter =np.abs(complex_filter)



filter_sigs = nf.ifft(complex_filter)

wf.write('out.wav',sample_rate,filter_sigs.real.astype('i2'))

