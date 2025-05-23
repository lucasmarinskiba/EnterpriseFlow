# Ejemplo: Mejorar autenticación en app/authentication.py
import streamlit as st
from passlib.hash import pbkdf2_sha256

def validate_password(password):
    # Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 especial
    if len(password) < 8: return False
    if not any(c.isupper() for c in password): return False
    if not any(c.isdigit() for c in password): return False
    if not any(c in "!@#$%^&*" for c in password): return False
    return True

def hash_password(password):
    return pbkdf2_sha256.hash(password)
