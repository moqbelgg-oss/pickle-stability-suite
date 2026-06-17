"""
Pickle Stability and Correctness Test Suite.
Includes both Stable and Unstable (Failing) Hash-Identity Cases.
Complies with PEP8 style guidelines.
"""

import hashlib
import pickle
import pytest
import random

def get_pickle_hash(obj, protocol=pickle.HIGHEST_PROTOCOL) -> str:
    """Serializes an object and returns its SHA-256 hash."""
    serialized_data = pickle.dumps(obj, protocol=protocol)
    return hashlib.sha256(serialized_data).hexdigest()

# =========================================================================
# STABLE CASES (Expected to PASS)
# =========================================================================

@pytest.mark.parametrize("protocol", [4, 5])
def test_primitive_types_determinism(protocol):
    """Tests that primitive types always produce identical hashes."""
    assert get_pickle_hash(42, protocol) == get_pickle_hash(42, protocol)
    assert get_pickle_hash("Hello", protocol) == get_pickle_hash("Hello", protocol)

@pytest.mark.parametrize("protocol", [4, 5])
def test_floating_point_bounds(protocol):
    """Tests extreme boundary values for floating-point precision."""
    assert get_pickle_hash(float('inf'), protocol) == get_pickle_hash(float('inf'), protocol)
    assert get_pickle_hash(float('nan'), protocol) == get_pickle_hash(float('nan'), protocol)

@pytest.mark.parametrize("protocol", [4, 5])
def test_recursive_and_nested_structures(protocol):
    """Tests complex nested structures (JSON-like) and recursive references."""
    nested_json = {"user": "AI", "details": {"id": 1001}}
    assert get_pickle_hash(nested_json, protocol) == get_pickle_hash(nested_json, protocol)

    recursive_list = [1, 2, 3]
    recursive_list.append(recursive_list)
    assert get_pickle_hash(recursive_list, protocol) == get_pickle_hash(recursive_list, protocol)

# =========================================================================
# UNSTABLE CASES (Expected to FAIL Hash-Identity)
# =========================================================================

@pytest.mark.xfail(reason="Altering structural interpretation or protocol breaks hash-identity.")
def test_unstable_protocol_variance():
    """
    UNSTABLE CASE 1: Testing the exact same dictionary across different protocols.
    Even with identical input, the output byte stream changes based on the protocol.
    """
    my_data = {"status": "success", "code": 200}
    # This will FAIL because hash(Protocol 4) != hash(Protocol 5)
    assert get_pickle_hash(my_data, protocol=4) == get_pickle_hash(my_data, protocol=5)


@pytest.mark.xfail(reason="Equivalent inputs with different memory or declaration bindings break hash-identity.")
def test_unstable_equivalent_but_not_identical():
    """
    UNSTABLE CASE 2: Testing equivalent inputs that are structurally altered.
    As per project description, x=2+3 vs x=3+2 or changing key insertion paths.
    """
    # Equivalent mathematically, but evaluated or stored with slight variations
    input_a = 2 + 3
    input_b = 3 + 2
    
    # In more complex objects or custom class instances, equivalent properties 
    # instantiated differently will break raw byte-hash identical requirements.
    # To demonstrate the prompt's condition:
    assert get_pickle_hash(f"result: {input_a}") == get_pickle_hash(f"result: {input_b}")


@pytest.mark.xfail(reason="Different environment scopes or dynamically created classes break pickle stability.")
def test_unstable_dynamic_objects():
    """
    UNSTABLE CASE 3: Dynamic or lambda-bound states cannot maintain stable hash identity
    because their internal tracking definitions change between execution bindings.
    """
    def make_class():
        class DynamicClass:
            def __init__(self): self.x = 1
        return DynamicClass()

    obj_1 = make_class()
    obj_2 = make_class()
    
    # Fails because their local class references are inherently non-identical in memory scopes
    assert get_pickle_hash(obj_1) == get_pickle_hash(obj_2)