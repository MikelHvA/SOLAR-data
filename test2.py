import matplotlib.pyplot as plt

# ----------------------------
# Data uit tabel
# ----------------------------
n_rps = [1.593, 3.510, 4.143, 4.989, 5.899]   # RPS (na reductie)
Vs = [0.646, 1.417, 1.666, 1.984, 2.398]      # m/s

# ----------------------------
# Constantes
# ----------------------------
Kq = 0.01808
rho = 1000
D = 0.355

# ----------------------------
# Functie
# ----------------------------
def bereken_Q(Kq, rho, n, D):
    return Kq * rho * n**2 * D**5

# ----------------------------
# Berekening
# ----------------------------
Q = [bereken_Q(Kq, rho, n, D) for n in n_rps]

# ----------------------------
# Plot
# ----------------------------
plt.figure()
plt.plot(Vs, Q, "o-", label="Model (tabel)")
plt.xlabel("Snelheid Vs (m/s)")
plt.ylabel("Q")
plt.title("Q als functie van snelheid")
plt.grid(True)
plt.legend()
plt.show()
