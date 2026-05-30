import os
from ecdsa import SECP256k1, SigningKey
from hashlib import sha256
# Визначаємо генератори G і H
curve = SECP256k1
G = curve.generator
order = curve.order
def hash_to_point(seed: str):
    h = int.from_bytes(sha256(seed.encode()).digest(), 'big') % order
    return h * G
H = hash_to_point("H")  # Імітація іншого генератора
# Pedersen Commitment: C = v*G + r*H
def pedersen_commit(value, blinding_factor):
    # Повертаємо кортеж: (об'єкт точки, вихідне значення, фактор приховування)
    return (value * G + blinding_factor * H, value, blinding_factor)
# Симуляція транзакцій
def simulate_transaction(inputs, outputs):
    print("==> Транзакція:")
    input_commitments_data = []
    output_commitments_data = []
    print("  Вхідні:")
    for val, bf in inputs:
        c_point, c_val, c_bf = pedersen_commit(val, bf)
        input_commitments_data.append((c_point, c_val, c_bf))
        # Форматуємо вивід вручну
        print(f"    Сума: {c_val}, Commitment: {c_val}×G+{c_bf}×H")
    print("  Вихідні:")
    for val, bf in outputs:
        c_point, c_val, c_bf = pedersen_commit(val, bf)
        output_commitments_data.append((c_point, c_val, c_bf))
        # Форматуємо вивід вручну
        print(f"    Сума: {c_val}, Commitment: {c_val}×G+{c_bf}×H")
    # Для розрахунків нам потрібні лише об'єкти точок
    sum_inputs = sum((data[0] for data in input_commitments_data), G * 0)
    sum_outputs = sum((data[0] for data in output_commitments_data), G * 0)
    # Якщо точка Jacobi — переводимо до афінної
    sum_inputs_affine = sum_inputs.to_affine() if hasattr(sum_inputs, 'to_affine') else sum_inputs
    sum_outputs_affine = sum_outputs.to_affine() if hasattr(sum_outputs, 'to_affine') else sum_outputs
    net_commitment = sum_inputs_affine + (-sum_outputs_affine)
    print("\n  Різниця (має бути 0 для збалансованої транзакції):")
    # Для net_commitment також можна було б реалізувати більш детальне представлення,
    # але оскільки це різниця, яка має бути 0, то її представлення як об'єкта точки є нормальним.
    print(f"    {net_commitment}\n")
# Приклад транзакцій до cut-through
tx1_output = (10, 7)  # (сума, blinding factor)
tx2_input = tx1_output  # цей вихід стає входом наступної транзакції
tx2_output1 = (6, 3)
tx2_output2 = (4, 4)
# До cut-through
print(">>> До cut-through:")
simulate_transaction(
    inputs=[tx2_input],
    outputs=[tx2_output1, tx2_output2]
)
# Після cut-through
print(">>> Після cut-through (скорочення розміру):")
simulate_transaction(
    inputs=[],
    outputs=[tx2_output1, tx2_output2]
)
