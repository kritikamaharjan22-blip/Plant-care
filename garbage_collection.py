# garbage_collection.py - Memory management utilities
import gc
import tensorflow as tf
import psutil
import os

def clear_memory():
    """Clear Python garbage and TensorFlow session"""
    gc.collect()
    tf.keras.backend.clear_session()
    gc.collect()
    print("🗑️ Memory cleared")

def print_memory():
    """Print current memory usage"""
    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"💾 Memory: {memory_mb:.1f} MB")
        return memory_mb
    except:
        return 0

def cleanup_variables(*args):
    """Delete multiple variables and clear memory"""
    for var in args:
        try:
            del var
        except:
            pass
    clear_memory()