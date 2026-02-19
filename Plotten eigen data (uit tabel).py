import matplotlib.pyplot as plt
import math

# ----------------------------
# Data uit tabel
# ----------------------------
plot_title = "Q als functie van snelheid (Fee-blad Vergelijken Methodes)"

n1_rps = [1.593, 3.510, 4.143, 4.989, 5.899, 9.999]   # RPS (na reductie)
n2_rps = [3.988,6.060,6.788,8.109]
Vs1 = [0.646, 1.417, 1.666, 1.984, 2.398, 3.985]      # m/s
Vs2 = [0.973,1.495,1.586,1.971]
Fs1 = [7.0, 25.2, 33.3, 45.4, 63.7, 162.5]
Fs2  = [34.70016397,115.2318598,136.6299702,256.9764349]
I  = [7, 24, 32, 45, 62, 175]
NmI = [0.76, 3.27, 4.25, 6.23, 8.65,24.41] #Alleen voor datasheet 
NmF = [0.95,1.91,2.49,3.46]
Fl = [3.708583767, 40.03293996, 67.06314935, 109.5293169,162.0441884,598.2228961]
Fl2 = [10.54,35.70,47.61,85.83]
Tk = [6.92,25.20,33.38,44.90,63.29,161.54]
Tk2 = [13.43,27.80,30.53,44.90]

# ----------------------------
# Constantes
# ----------------------------
KTI = 0.0848
KTF = 0.05
KqI = 0.01808
KqF = 0.005
rho = 1000
D = 0.355

# ----------------------------
# Functie
# ----------------------------
def berekenen_T2(KTI, rho, n, D):
    return KTI * rho * n**2 * D**4

def berekenen_T3(KTF, rho, n, D):
    return KTF * rho * n**2 * D**4

def bereken_Q(KqI, rho, n, D):
    return KqI * rho * n**2 * D**5

def bereken_Q2(KqF, rho, n, D):
    return KqF * rho * n**2 * D**5

def bereken_Q3(Fs1, Vs1, n_rps):
    omega = 2 * math.pi * n_rps  # rad/s
    return (Fs1 * Vs1) / omega
def bereken_Q4(Fs2, Vs2, n_rps):
    omega = 2 * math.pi * n_rps  # rad/s
    return (Fs2 * Vs2) / omega

# ----------------------------
# Berekening
# ----------------------------

T2 = [berekenen_T2(KTI, rho, n, D) for n in n1_rps]
T3 = [berekenen_T3(KTF, rho, n, D) for n in n2_rps]
Q1 = [bereken_Q(KqI, rho, n, D) for n in n1_rps]
Q2 = [bereken_Q2(KqF, rho, n, D) for n in n2_rps] 
Q3 = [bereken_Q3(Fs_i, Vs_i, n_i) for Fs_i, Vs_i, n_i in zip(Fs1, Vs1, n1_rps)]
Q4 = [bereken_Q4(Fs_i, Vs_i, n_i) for Fs_i, Vs_i, n_i in zip(Fs2, Vs2, n2_rps)]

# ----------------------------
# Plot
# ----------------------------
plt.figure()

#plt.plot(Vs1, NmI, "o-", label="SOLAR(Incapa-blad / Methode 1)") #Methode 1 / Incapablad
plt.plot(Vs2, NmF, "o-", label="SOLAR(Fee-Blad / Methode 1)") #Methode 1 / Incapablad
#plt.plot(Vs2, T3, "o-", label="SOLAR(Fee-blad / Methode 1)")
#plt.plot(Vs1, T2, "o-", label="SOLAR(Incapa-blad / Methode 1)") #Methoode 1 / Incapablad
#plt.plot(Vs1, Q1, "o-", label="SOLAR(Methode 2)") #Methode 2 / Incapablad
plt.plot(Vs2, Q2, "o-", label="SOLAR(Fee-blad / Methode 2)")
#plt.plot(Vs1, Q3, "o-", label="SOLAR(Incapa-blad / Methode 3)") #Methode 3 / Incapablad
plt.plot(Vs2, Q4, "o-", label="SOLAR(Fee-blad / Methode 3)") #Methode 3 / Incapablad
#plt.plot(Vs1, Fl, "o-", label="SOLAR(Incapablad / Methode 2)") #Methode 2 / Incapablad
#plt.plot(Vs2, Fl2, "o-", label="SOLAR(Fee-blad / Methode 2)") #Methode 2 / Feeblad
#plt.plot(Vs1, Tk, "o-", label="SOLAR(Incapa-blad / Trekproef)") #Methode 2 / Feeblad
#plt.plot(Vs2, Tk2, "o-", label="SOLAR(Fee-blad / Trekproef)") #Methode 2 / Feeblad
plt.xlabel("Snelheid Vs (m/s)")
plt.ylabel("Q (Nm)")
plt.title(plot_title)
plt.grid(True)
plt.legend()
plt.savefig(plot_title + ".png", dpi=300, bbox_inches="tight")
plt.show()

