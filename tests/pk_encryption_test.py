import importlib
import pytest
import olm

from vodozemac import Curve25519SecretKey, Curve25519PublicKey, PkEncryption, PkDecryption, PkDecodeException

CLEARTEXT = b"test"

class TestClass(object):
    def test_encrypt_decrypt(self):
        d = PkDecryption()
        e = PkEncryption.from_key(d.public_key)
        enc = e.encrypt(CLEARTEXT)
        mac = enc.mac
        decoded = d.decrypt(enc)
        assert decoded == CLEARTEXT

    def test_encrypt_message_attr(self):
        d = PkDecryption()
        e = PkEncryption.from_key(d.public_key)
        pub_key = d.public_key
        encrypts = PkEncryption.from_key(pub_key)
        enc_message = encrypts.encrypt(CLEARTEXT)
        
        mac = enc_message.mac
        ciphertext = enc_message.ciphertext
        ephemeral_key = enc_message.ephemeral_key

        assert mac is not None
        assert ciphertext is not None
        assert ephemeral_key is not None


    def test_olm_api_compatibility(self):
        
        # [PSEUDO CODE]

        pub_key = "abcdefghijklmnopqrstuvwxyz"

        # Old olm implementation
        encrypts = olm.pk.PkEncryption(pub_key)
        olm_message = encrypts.encrypt(CLEARTEXT)

        # New vodozemac implementation (PUB KEY is not SAME here)
        d = PkDecryption.from_key(pub_key)
        pub_key = d.public_key
        encrypts = PkEncryption.from_key(pub_key)
        vodozemac_message = encrypts.encrypt(CLEARTEXT)

        assert olm_message.ciphertext == vodozemac_message.ciphertext
        assert olm_message.mac == vodozemac_message.mac
        assert olm_message.ephemeral_key == vodozemac_message.ephemeral_key

    def test_encrypt_decrypt_with_wrong_key(self):
        wrong_e = PkEncryption.from_key(PkDecryption().public_key)
        with pytest.raises(PkDecodeException, match="MAC tag mismatch"):
            PkDecryption().decrypt(wrong_e.encrypt(CLEARTEXT))

    def test_encrypt_decrypt_with_serialized_keys(self):
        secret_key = Curve25519SecretKey()
        secret_key_bytes = secret_key.to_bytes()
        public_key_bytes = secret_key.public_key().to_bytes()

        d = PkDecryption.from_key(Curve25519SecretKey.from_bytes(secret_key_bytes))
        e = PkEncryption.from_key(Curve25519PublicKey.from_bytes(public_key_bytes))

        decoded = d.decrypt(e.encrypt(CLEARTEXT))
        assert decoded == CLEARTEXT
