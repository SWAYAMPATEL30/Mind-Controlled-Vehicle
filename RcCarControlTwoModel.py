"""
Program takes real time inputs from the user and gives out predictions with the use of 2 models
Electrode placements: Black(-in) and Red(+)on forehead, Yellow(Ref) on ear lobe
"""

import serial
import matplotlib.pyplot as plt
import time
import numpy as np
import csv
import joblib

state_model = joblib.load('Normal0Focus1EyesC1EveryoneP5.pkl')
diff_model = joblib.load('Focus1EyesC0EveryoneP5.pkl')

#Creating an instance object 
serialInst = serial.Serial("COM5", 500000)

#Creating a remote for controlling the car
serialRemote = serial.Serial("COM4", 115200)

#Sampling rate (that is 200 samples per second)
fs = 100 
frequencies = None
fft_result = None
prev_val_counter = 5 #Defines the no. of past inputs to give for prediction
buffer_period = 100 #Time for buffer to start the process
eeg_data = []
focus_state = 0  #0 stands for no focus & 1 stands for full focus
prev = []
time_ignore = 0

print("Program start")

start = time.time()

#First fill the EEG data with 200 samples
while True:
    if len(eeg_data) == 100:
        break
    if serialInst.in_waiting:
        try:
            bytes = serialInst.read(2)
            received_value = int(bytes[0] + (bytes[1] << 8))
            eeg_data.append(received_value)
        except Exception as e:
            print(e)

        endtime = time.time()

print(f"The length of EEG data {len(eeg_data)}")
print(f"The time to fill 100 samples {endtime-start}")

fft_result = np.fft.fft(eeg_data)
frequencies = np.fft.fftfreq(len(eeg_data), 1/fs)
magnitude = np.abs(fft_result)

#Counter Declaration
counter = 0

while True:
    eyeParam = []
    try:
        #Popping 10 samples from the list and adding new samples into it
        #print(f"*****{serialInst.in_waiting}*******")
        if serialInst.in_waiting > 20:
            print(counter)
            starttime = time.time()
            counter += 1
            eeg_data = eeg_data[10:]
            for y in range(10):
                bytes = serialInst.read(2)
                received_value = int(bytes[0] + (bytes[1] << 8))
                eeg_data.append(received_value)
            
            #print(eeg_data)


            #Performing FFT and limiting to 8-13 Hz
            fft_result = np.fft.fft(eeg_data)
            frequencies = np.fft.fftfreq(len(eeg_data), 1/fs)
            magnitude = np.abs(fft_result)
            phase = np.angle(fft_result)
            #print(phase)
            #print(frequencies)
            #print(magnitude)

            #Low alpha hertz frequencies
            mask = (frequencies >= 8) & (frequencies <= 9)
            filtered_low_alpha_results = fft_result[mask]
            phase = np.angle(filtered_low_alpha_results)
            #Averaging both the values of low alpha waves
            magnitude1 = np.abs(filtered_low_alpha_results)
            lowAlpha = np.mean(magnitude1)
            lowAlphaPhase = np.mean(phase)
            eyeParam.append(lowAlpha)
            eyeParam.append(lowAlphaPhase)

            #High alpha hertz frequencies
            mask = (frequencies >= 10) & (frequencies <= 12)
            filtered_high_alpha_results = fft_result[mask]
            phase = np.angle(filtered_high_alpha_results)
            #Averaging both the values of high alpha waves
            magnitude2 = np.abs(filtered_high_alpha_results)
            highAlpha = np.mean(magnitude2)
            highAlphaPhase = np.mean(phase)
            eyeParam.append(highAlpha)
            eyeParam.append(highAlphaPhase)

            #Low Beta hertz frequencies
            mask = (frequencies >= 13) & (frequencies <= 17)
            filtered_low_beta_results = fft_result[mask]
            phase = np.angle(filtered_low_beta_results)
            #Averaging both the values of low beta waves
            magnitude3 = np.abs(filtered_low_beta_results)
            lowBeta = np.mean(magnitude3)
            lowBetaPhase = np.mean(phase)
            eyeParam.append(lowBeta)
            eyeParam.append(lowBetaPhase)

            #High Beta hertz frequencies
            mask = (frequencies >= 18) & (frequencies <= 30)
            filtered_high_beta_results = fft_result[mask]
            phase = np.angle(filtered_high_beta_results)
            #Averaging both the values of low beta waves
            magnitude4 = np.abs(filtered_high_beta_results)
            highBeta = np.mean(magnitude4)
            highBetaPhase = np.mean(phase)
            eyeParam.append(highBeta)
            eyeParam.append(highBetaPhase)

            #Low Gamma hertz frequencies
            mask = (frequencies >= 30) & (frequencies <= 40)
            filtered_low_gamma_results = fft_result[mask]
            phase = np.angle(filtered_low_gamma_results)
            #Averaging both the values of low alpha waves
            magnitude5 = np.abs(filtered_low_gamma_results)
            lowGamma = np.mean(magnitude5)
            lowGammaPhase = np.mean(phase)
            eyeParam.append(lowGamma)
            eyeParam.append(lowGammaPhase)

            #High Gamma hertz frequencies
            mask = (frequencies >= 31) & (frequencies <= 49)
            filtered_high_gamma_results = fft_result[mask]
            phase = np.angle(filtered_high_gamma_results)
            #Averaging both the values of low alpha waves
            magnitude6 = np.abs(filtered_high_gamma_results)
            highGamma = np.mean(magnitude6)
            highGammaPhase = np.mean(phase)
            eyeParam.append(highGamma)
            eyeParam.append(highGammaPhase)

            endtime = time.time()

            """
            print(f"\n\n\nLength of EEG Data {len(eeg_data)}")
            print(f"Power of Low Alpha Waves {lowAlpha}")
            print(f"Time duration {endtime-starttime}")
            print(f"Iteration {counter}")

            print(f"Power of Low Alpha Waves {lowAlpha}")
            print(f"Phase of Low Alpha waves {lowAlphaPhase}")

            print(f"Power of High Alpha Waves {highAlpha}")
            print(f"Phase of High Alpha waves {highAlphaPhase}")

            print(f"Power of Low Beta Waves {lowBeta}")
            print(f"Phase of Low Beta waves {lowBetaPhase}")

            print(f"Power of High Beta Waves {highBeta}")
            print(f"Phase of High Beta waves {highBetaPhase}")

            print(f"Power of Low Gamma Waves {lowGamma}")
            print(f"Phase of Low Gamma waves {lowGammaPhase}")

            print(f"Power of High Gamma Waves {highGamma}")
            print(f"Phase of High Gamma waves {highGammaPhase}")

            print(f"Time duration {endtime-starttime}")
            print(f"Iteration {counter}")
            """
            if counter > (buffer_period-prev_val_counter) and counter < (buffer_period+1):
                prev.append((lowAlpha+highAlpha)/2)
                prev.append((lowBeta+highBeta)/2)
                prev.append((lowGamma+highGamma)/2) 

            #Start predicting the status of eyes
            if counter > buffer_period:

                #Collection all the parameter inputs for the model and loading it into a array
                eyeParam.extend(prev)
                print(eyeParam)

                #Giving all parameters to both the models
                state_prediction = state_model.predict([eyeParam])
                print(f"Predicted value of First Model ", state_prediction)
                if int(state_prediction) != 0:
                    diff_prediction = diff_model.predict([eyeParam])
                    print(f"Predicted value of Second Model",diff_prediction)
                    if int(diff_prediction) == 1:
                        time_ignore += 1
                        focus_state = 1
                        serialRemote.write('F\n'.encode())
                        print("Data Sent >>>> FFFFFFFFFFFFFFF")
                    else:
                        if focus_state == 1 and time_ignore > 15:
                            focus_state = 0
                            time_ignore = 0
                            serialRemote.write('S\n'.encode())
                            print("Data Sent >>>>>>>>> SSSSSSSSSSSSSSSSS")
                        elif focus_state == 1:
                            time_ignore += 1
                else:
                    if focus_state == 1:
                        time_ignore += 1

                if len(prev) == int(prev_val_counter*3):
                    prev.pop(0)
                    prev.pop(0)
                    prev.pop(0)
                    prev.append((lowAlpha+highAlpha)/2)
                    prev.append((lowBeta+highBeta)/2)
                    prev.append((lowGamma+highGamma)/2) 

                print(f"FOCUS STATE {focus_state}")
                print(f"TIME IGNORE {time_ignore}")

    except Exception as e:
        print(e)
        break

print("The Program has been terminated!")






        



