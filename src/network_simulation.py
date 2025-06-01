import math
import random
import os


RESULT_DIR = "results"


def ensure_results_dir():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)


def simulate_model_9_3():
    """Generate asymmetric resonance strengths over time."""
    ensure_results_dir()
    q_m = 0.8
    q_e = 0.6
    epsilon = 0.1

    def f(x, y):
        return x * y

    lines = []
    for t in range(10):
        lambda0 = math.sin(float(t))
        lam_me = lambda0 + epsilon * 0.01 * f(q_m, q_e)
        lam_em = lambda0 + epsilon * -0.01 * f(q_e, q_m)
        line = f"t={t} lambda_m->e={lam_me:.6f} lambda_e->m={lam_em:.6f}"
        print(line)
        lines.append(line)

    out_path = os.path.join(RESULT_DIR, "model_9_3.txt")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines))


def _init_lambda_matrix(n):
    mat = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0.0)
            else:
                row.append(random.uniform(0.01, 0.05))
        mat.append(row)
    return mat


def _stats(mat):
    flat = [v for row in mat for v in row]
    avg = sum(flat) / len(flat)
    neg = sum(1 for v in flat if v < 0.0)
    lam_max = max(flat)
    lam_min = min(flat)
    return avg, neg, lam_min, lam_max


def simulate_model_10_3():
    """10-node logistic evolution of lambda_ij."""
    ensure_results_dir()
    n = 10
    dt = 0.1
    total_t = 5.0
    r = 1.0
    c = 0.05

    mat = _init_lambda_matrix(n)
    lines = []
    steps = int(total_t / dt) + 1
    for step in range(steps):
        t = step * dt
        avg, neg, lam_min, lam_max = _stats(mat)
        line = f"t={t:.1f} avg={avg:.6f} min={lam_min:.6f} max={lam_max:.6f} neg_count={neg}"
        print(line)
        lines.append(line)
        if step == steps - 1:
            break
        new_mat = []
        for i in range(n):
            new_row = []
            for j in range(n):
                lam = mat[i][j]
                comp = 0.0
                for k in range(n):
                    if k != i and k != j:
                        comp += c * mat[i][k] * mat[k][j]
                new_val = lam + dt * (r * lam * (1 - lam) - comp)
                new_row.append(new_val)
            new_mat.append(new_row)
        mat = new_mat

    out_path = os.path.join(RESULT_DIR, "model_10_3_stats.txt")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines))


def simulate_model_10_6():
    """30-node network statistics written in CSV."""
    ensure_results_dir()
    n = 30
    dt = 0.1
    total_t = 3.0
    r = 1.0
    c = 0.05

    mat = _init_lambda_matrix(n)
    steps = int(total_t / dt) + 1
    out_path = os.path.join(RESULT_DIR, "model_10_6_stats.csv")
    with open(out_path, "w") as fh:
        header = "time,avg_lambda,neg_count,degree\n"
        fh.write(header)
        print(header.strip())
        for step in range(steps):
            t = step * dt
            flat = [v for row in mat for v in row]
            avg = sum(flat) / len(flat)
            neg = sum(1 for v in flat if v < 0.0)
            edges = sum(1 for i in range(n) for j in range(n) if i != j and mat[i][j] > 0.0)
            degree = edges / float(n)
            line = f"{t:.1f},{avg:.6f},{neg},{degree:.2f}"
            print(line)
            fh.write(line + "\n")
            if step == steps - 1:
                break
            new_mat = []
            for i in range(n):
                new_row = []
                for j in range(n):
                    lam = mat[i][j]
                    comp = 0.0
                    for k in range(n):
                        if k != i and k != j:
                            comp += c * mat[i][k] * mat[k][j]
                    new_val = lam + dt * (r * lam * (1 - lam) - comp)
                    new_row.append(new_val)
                new_mat.append(new_row)
            mat = new_mat

if __name__ == "__main__":
    simulate_model_9_3()
    simulate_model_10_3()
    simulate_model_10_6()
