class MasterPassword:
    """
    Basic ideas:

    1. master password can only be stored in the memory for long time in the form which cannot be converted back to the
       plaintext of the master password, i.e. master password can be stored in the form of:

       a. hash digest
       b. salted hash digest

       cannot be stored in the form of:

       a. plaintext (except temporary storage, like user input)
       b. invertible encryption (either symmetric or asymmetric encryption)

    """

    def encrypt(self, message):
        """
        Use master password (actually its hash) to encrypt a message
        """
        pass
