from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt_AES(plaintext, key):
    """
    Encrypts the plaintext using AES encryption in CBC mode.
    The IV is generated internally and prepended to the ciphertext.
    
    Args:
        plaintext (str): The text to encrypt.
        key (bytes): The encryption key (must be 16, 24, or 32 bytes long).

    Returns:
        bytes: The IV-prepended ciphertext.
    """
    data = plaintext.encode('utf-8')
    
    iv = get_random_bytes(AES.block_size)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    
    return iv + ciphertext

def decrypt_AES(encrypted, key):
    """
    Decrypts the IV-prepended ciphertext using AES decryption in CBC mode.
    
    Args:
        encrypted (bytes): The IV-prepended ciphertext.
        key (bytes): The decryption key (must be the same as the encryption key).

    Returns:
        str: The decrypted plaintext.
    """
    iv = encrypted[:AES.block_size]
    ciphertext = encrypted[AES.block_size:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    return decrypted_data.decode('utf-8')

if __name__ == "__main__":
    key = get_random_bytes(16) 
    print(type(key), key)
    message = "This is a secret message with IV used only in the algorithm! This is a secret message with IV used only in the algorithm! This is a secret message with IV used only in the algorithm!"
    
    encrypted_message = encrypt_AES(message, key)
    print(type(encrypted_message), encrypted_message)
    print("Encrypted Message (hex):", encrypted_message.hex())
    
    decrypted_message = decrypt_AES(encrypted_message, key)
    print("Decrypted Message:", decrypted_message)
