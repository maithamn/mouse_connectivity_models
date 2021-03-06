from __future__ import division

import pytest
import numpy as np
from numpy.testing \
    import assert_array_equal, assert_array_almost_equal, assert_raises

from mcmodels.models.voxel import VoxelConnectivityArray


@pytest.fixture(scope="module")
def weights():
    return np.random.choice(4, size=(10,5) )


@pytest.fixture(scope="module")
def nodes():
    # more probability of zero (more realistic)
    return np.random.choice(4, size=(5,20), p=(.7,.1,.1,.1))


@pytest.fixture(scope="function")
def true_array(weights, nodes):
    return weights.dot(nodes)


@pytest.fixture(scope="function")
def voxel_array(weights, nodes):
    return VoxelConnectivityArray(weights=weights, nodes=nodes)


# ============================================================================
# constructors
# ============================================================================
def test_from_csv(tmpdir, weights, nodes):
    # ------------------------------------------------------------------------
    # test
    f1 = tmpdir.join("weights.csv")
    f2 = tmpdir.join("nodes.csv")

    # get filenames not localpath objects
    f1, f2 = map(str, (f1, f2))

    np.savetxt(f1, weights, delimiter=",")
    np.savetxt(f2, nodes, delimiter=",")

    va = VoxelConnectivityArray.from_csv(f1, f2)

    assert_array_equal(weights, va.weights)
    assert_array_equal(nodes, va.nodes)


def test_from_npy(tmpdir, weights, nodes):
    # ------------------------------------------------------------------------
    # test
    f1 = tmpdir.join("weights.npy")
    f2 = tmpdir.join("nodes.npy")

    # get filenames not localpath objects
    f1, f2 = map(str, (f1, f2))

    np.save(f1, weights)
    np.save(f2, nodes)

    voxel_array = VoxelConnectivityArray.from_npy(f1, f2)

    assert_array_equal(weights, voxel_array.weights)
    assert_array_equal(nodes, voxel_array.nodes)


# ============================================================================
# dunder methods
# ============================================================================
def test_init():
    # ------------------------------------------------------------------------
    # test
    # not both arrays
    assert_raises(AttributeError, VoxelConnectivityArray, [1], np.array([1]))

    # wrong sizes
    a, b = map(np.ones, [(10, 10), (100, 10)])
    assert_raises(ValueError, VoxelConnectivityArray, a, b)

    # dtype mismatch
    b = np.ones((10, 10)).astype(np.float32)
    assert_raises(ValueError, VoxelConnectivityArray, a, b)


def test_getitem(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test
    assert_array_equal(voxel_array[3:5, 0], true_array[3:5, 0])
    assert_array_equal(voxel_array[2:6], true_array[2:6])
    assert_array_equal(voxel_array[:, 2:6], true_array[:, 2:6])
    assert_array_equal(voxel_array[-1], true_array[-1])

    idx = [1, 3, 7]
    assert_array_equal(voxel_array[idx], true_array[idx])


def test_len(weights, nodes):
    # ------------------------------------------------------------------------
    # test
    model = VoxelConnectivityArray(weights, nodes)

    assert len(weights) == len(model)


# ============================================================================
# properties
# ============================================================================
def test_dtype(weights, nodes):
    # ------------------------------------------------------------------------
    # test
    model = VoxelConnectivityArray(weights, nodes)

    assert model.dtype == weights.dtype
    assert model.dtype == nodes.dtype


def test_shape(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test
    assert voxel_array.shape == true_array.shape


def test_size(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test
    assert( voxel_array.size == true_array.size )


def test_T(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test
    assert voxel_array.shape == voxel_array.T.shape[::-1]


# ============================================================================
# methods
# ============================================================================
def test_transpose(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test
    assert_array_equal(voxel_array.T[:], true_array.T)


def test_astype(voxel_array):
    # ------------------------------------------------------------------------
    # test
    voxel_array = voxel_array.astype(np.float16)

    assert voxel_array.dtype == np.float16
    assert voxel_array.weights.dtype == np.float16
    assert voxel_array.nodes.dtype == np.float16


def test_sum(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test
    assert voxel_array.sum() == true_array.sum()
    assert_array_almost_equal(voxel_array.sum(axis=1), true_array.sum(axis=1))
    assert_array_almost_equal(voxel_array.sum(axis=-1), true_array.sum(axis=-1))
    assert_array_almost_equal(voxel_array.sum(axis=0), true_array.sum(axis=0))
    assert_raises( IndexError, voxel_array.sum, axis=2)


def test_mean(voxel_array, true_array):
    # ------------------------------------------------------------------------
    # test

    assert voxel_array.mean() == true_array.mean()
    assert_array_almost_equal(voxel_array.mean(axis=1), true_array.mean(axis=1))
    assert_array_almost_equal(voxel_array.mean(axis=-1), true_array.mean(axis=-1))
    assert_array_almost_equal(voxel_array.mean(axis=0), true_array.mean(axis=0))
    assert_raises(IndexError, voxel_array.mean, axis=2)


def test_iterrows(true_array, voxel_array):
    # ------------------------------------------------------------------------
    # test
    for i, row in enumerate(voxel_array.iterrows()):
        assert_array_equal(row, true_array[i])


def test_itercolumns(true_array, voxel_array):
    # ------------------------------------------------------------------------
    # test
    for j, column in enumerate(voxel_array.itercolumns()):
        assert_array_equal(column, true_array[:, j])


def test_iterrows_blocked(true_array, voxel_array):
    # ------------------------------------------------------------------------
    # test

    rows = np.array_split(np.arange(true_array.shape[0]), 1)
    for i, block in enumerate(voxel_array.iterrows_blocked(n_blocks=1)):
        assert_array_equal(block, true_array[rows[i]])

    # ------------------------------------------------------------------------
    # test
    rows = np.array_split(np.arange(true_array.shape[0]), 10)
    for i, block in enumerate(voxel_array.iterrows_blocked(n_blocks=10)):
        assert_array_equal(block, true_array[rows[i]])

    # ------------------------------------------------------------------------
    # test
    func = voxel_array.iterrows_blocked(n_blocks=0)
    assert_raises(ValueError, next, func)

    # ------------------------------------------------------------------------
    # test
    func = voxel_array.iterrows_blocked(n_blocks=11)
    assert_raises(ValueError, next, func)


def test_itercolumns_blocked(true_array, voxel_array):
    # ------------------------------------------------------------------------
    # test
    cols = np.array_split(np.arange(true_array.shape[1]), 1)
    for i, block in enumerate(voxel_array.itercolumns_blocked(n_blocks=1)):
        assert_array_equal(block, true_array[:, cols[i]])

    # ------------------------------------------------------------------------
    # test
    cols = np.array_split(np.arange(true_array.shape[1]), 20)
    for i, block in enumerate(voxel_array.itercolumns_blocked(n_blocks=20)):
        assert_array_equal(block, true_array[:, cols[i]])

    # ------------------------------------------------------------------------
    # test
    func = voxel_array.itercolumns_blocked(n_blocks=0)
    assert_raises(ValueError, next, func)

    # ------------------------------------------------------------------------
    # test
    func = voxel_array.itercolumns_blocked(n_blocks=21)
    assert_raises(ValueError, next, func)
