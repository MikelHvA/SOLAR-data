import matplotlib.pyplot as plt

# ----------------------------
# Gegeven data uit tabel
# ----------------------------
n_rps = [1.59, 3.51, 4.14, 4.99, 5.90]   # RPS (na reductie)

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
# Berekeningen
# ----------------------------
Q = [bereken_Q(Kq, rho, n, D) for n in n_rps]

# RPS → RPM voor de x-as
rpm = [n * 60 for n in n_rps]

# ----------------------------
# Plot
# ----------------------------
plt.figure()
plt.plot(rpm, Q, "o-", label="Model")
plt.xlabel("RPM")
plt.ylabel("Q")
plt.title("Q als functie van RPM (tabelwaarden)")
plt.grid(True)
plt.legend()
plt.show()
