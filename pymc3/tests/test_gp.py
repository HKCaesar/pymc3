#  pylint:disable=unused-variable
from .helpers import SeededTest
import unittest
from pymc3 import Model, gp, sample, Uniform
import theano
import theano.tensor as tt
import numpy as np

class TestZero(unittest.TestCase):
    def test_value(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            zero_mean = gp.mean.Zero()
        M = theano.function([], zero_mean(X))()
        self.assertTrue(np.all(M==0))
        self.assertSequenceEqual(M.shape, (10,1))

class TestConstant(unittest.TestCase):
    def test_value(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            const_mean = gp.mean.Constant(6)
        M = theano.function([], const_mean(X))()
        self.assertTrue(np.all(M==6))
        self.assertSequenceEqual(M.shape, (10,1))

class TestLinearMean(unittest.TestCase):
    def test_value(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            linear_mean = gp.mean.Linear(2, 0.5)
        M = theano.function([], linear_mean(X))()
        self.assertAlmostEqual(M[1,0], 0.7222, 3)


class TestCovAdd(unittest.TestCase):
    def test_symadd_cov(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov1 = gp.cov.ExpQuad(1, 0.1)
            cov2 = gp.cov.ExpQuad(1, 0.1)
            cov = cov1 + cov2
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 2*0.53940, 3)

    def test_rightadd_scalar(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            a = 1
            cov = gp.cov.ExpQuad(1, 0.1) + a
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 1 + 0.53940, 3)

    def test_leftadd_scalar(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            a = 1
            cov = a + gp.cov.ExpQuad(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 1 + 0.53940, 3)

    def test_rightadd_matrix(self):
        X = np.linspace(0,1,10)[:,None]
        M = 2 * np.ones((10,10))
        with Model() as model:
            cov = gp.cov.ExpQuad(1, 0.1) + M
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 2 + 0.53940, 3)

    def test_leftprod_matrix(self):
        X = np.linspace(0,1,3)[:,None]
        M = np.array([[1,2,3],[2,1,2],[3,2,1]])
        with Model() as model:
            cov = M + gp.cov.ExpQuad(1, 0.1)
            cov_true = gp.cov.ExpQuad(1, 0.1) + M
        K = theano.function([], cov(X))()
        K_true = theano.function([], cov_true(X))()
        self.assertTrue(np.allclose(K, K_true))


class TestCovProd(unittest.TestCase):
    def test_symprod_cov(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov1 = gp.cov.ExpQuad(1, 0.1)
            cov2 = gp.cov.ExpQuad(1, 0.1)
            cov = cov1 * cov2
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.53940 * 0.53940, 3)

    def test_rightprod_scalar(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            a = 2
            cov = gp.cov.ExpQuad(1, 0.1) * a
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 2 * 0.53940, 3)

    def test_leftprod_scalar(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            a = 2
            cov = a * gp.cov.ExpQuad(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 2 * 0.53940, 3)

    def test_rightprod_matrix(self):
        X = np.linspace(0,1,10)[:,None]
        M = 2 * np.ones((10,10))
        with Model() as model:
            cov = gp.cov.ExpQuad(1, 0.1) * M
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 2 * 0.53940, 3)

    def test_leftprod_matrix(self):
        X = np.linspace(0,1,3)[:,None]
        M = np.array([[1,2,3],[2,1,2],[3,2,1]])
        with Model() as model:
            cov = M * gp.cov.ExpQuad(1, 0.1)
            cov_true = gp.cov.ExpQuad(1, 0.1) * M
        K = theano.function([], cov(X))()
        K_true = theano.function([], cov_true(X))()
        self.assertTrue(np.allclose(K, K_true))

    def test_multiops(self):
        X = np.linspace(0,1,3)[:,None]
        M = np.array([[1,2,3],[2,1,2],[3,2,1]])
        with Model() as model:
            cov1 = 3 + gp.cov.ExpQuad(1, 0.1) + M * gp.cov.ExpQuad(1, 0.1) * M * gp.cov.ExpQuad(1, 0.1)
            cov2 = gp.cov.ExpQuad(1, 0.1) * M * gp.cov.ExpQuad(1, 0.1) * M + gp.cov.ExpQuad(1, 0.1) + 3
        K1 = theano.function([], cov1(X))()
        K2 = theano.function([], cov2(X))()
        self.assertTrue(np.allclose(K1, K2))


class TestCovSliceDim(unittest.TestCase):
    def test_slice1(self):
        X = np.linspace(0,1,30).reshape(10,3)
        with Model() as model:
            cov = gp.cov.ExpQuad(3, 0.1, active_dims=[0,0,1])
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.20084298, 3)

    def test_slice2(self):
        X = np.linspace(0,1,30).reshape(10,3)
        with Model() as model:
            cov = gp.cov.ExpQuad(3, [0.1, 0.1], active_dims=[False, True, True])
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.34295549, 3)

    def test_slice3(self):
        X = np.linspace(0,1,30).reshape(10,3)
        with Model() as model:
            cov = gp.cov.ExpQuad(3, np.array([0.1, 0.1]), active_dims=[False, True, True])
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.34295549, 3)

    def test_diffslice(self):
        X = np.linspace(0,1,30).reshape(10,3)
        with Model() as model:
            cov = gp.cov.ExpQuad(3, 0.1, [1, 0, 0]) + gp.cov.ExpQuad(3, [0.1, 0.2, 0.3])
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.683572, 3)

    def test_raises(self):
        lengthscales = 2.0
        with self.assertRaises(ValueError):
            gp.cov.ExpQuad(1, lengthscales, [True, False])
            gp.cov.ExpQuad(2, lengthscales, [True])


class TestStability(unittest.TestCase):
    def test_stable(self):
        X = np.random.uniform(low=320., high=400., size=[2000,2])
        with Model() as model:
            cov = gp.cov.ExpQuad(2, 0.1)
        dists = theano.function([], cov.square_dist(X, X))()
        self.assertFalse(np.any(dists < 0))


class TestExpQuad(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.ExpQuad(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.53940, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.53940, 3)

    def test_2d(self):
        X = np.linspace(0,1,10).reshape(5,2)
        with Model() as model:
            cov = gp.cov.ExpQuad(2, 0.5)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.820754, 3)

    def test_2dard(self):
        X = np.linspace(0,1,10).reshape(5,2)
        with Model() as model:
            cov = gp.cov.ExpQuad(2, np.array([1, 2]))
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.969607, 3)


class TestRatQuad(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.RatQuad(1, 0.1, 0.5)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.66896, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.66896, 3)


class TestExponential(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.Exponential(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.57375, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.57375, 3)


class TestMatern52(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.Matern52(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.46202, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.46202, 3)


class TestMatern32(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.Matern32(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.42682, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.42682, 3)


class TestCosine(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.Cosine(1, 0.1)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], -0.93969, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], -0.93969, 3)


class TestLinear(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.Linear(1, 0.5)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.19444, 3)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.19444, 3)


class TestPolynomial(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        with Model() as model:
            cov = gp.cov.Polynomial(1, 0.5, 2, 0)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.03780, 4)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.03780, 4)


class TestWarpedInput(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0,1,10)[:,None]
        def warp_func(x, a, b, c):
            return x + (a * tt.tanh(b * (x - c)))
        with Model() as model:
            cov_m52 = gp.cov.Matern52(1, 0.2)
            cov = gp.cov.WarpedInput(1, warp_func=warp_func, args=(1,10,1), cov_func=cov_m52)
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[0,1], 0.79593, 4)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[0,1], 0.79593, 4)

    def test_raises(self):
        cov_m52 = gp.cov.Matern52(1, 0.2)
        with self.assertRaises(TypeError):
            gp.cov.WarpedInput(1, cov_m52, "str is not callable")
        with self.assertRaises(TypeError):
            gp.cov.WarpedInput(1, "str is not Covariance object", lambda x: x)


class TestGibbs(unittest.TestCase):
    def test_1d(self):
        X = np.linspace(0, 2, 10)[:,None]
        def tanh_func(x, x1, x2, w, x0):
            return (x1 + x2) / 2.0 - (x1 - x2) / 2.0 * tt.tanh((x - x0) / w)
        with Model() as model:
            cov = gp.cov.Gibbs(1, tanh_func, args=(0.05, 0.6, 0.4, 1.0))
        K = theano.function([], cov(X))()
        self.assertAlmostEqual(K[2,3], 0.136683, 4)
        K = theano.function([], cov(X,X))()
        self.assertAlmostEqual(K[2,3], 0.136683, 4)

    def test_raises(self):
        with self.assertRaises(TypeError):
            gp.cov.Gibbs(1, "str is not callable")
        with self.assertRaises(NotImplementedError):
            gp.cov.Gibbs(2, lambda x: x)
        with self.assertRaises(NotImplementedError):
            gp.cov.Gibbs(3, lambda x: x, active_dims=[True, True, False])


class TestHandleArgs(unittest.TestCase):
    def test_handleargs(self):
        def func_noargs(x):
            return x
        def func_onearg(x, a):
            return x + a
        def func_twoarg(x, a, b):
            return x + a + b
        x = 100
        a = 2
        b = 3
        func_noargs2 = gp.cov.handle_args(func_noargs, None)
        func_onearg2 = gp.cov.handle_args(func_onearg, a)
        func_twoarg2 = gp.cov.handle_args(func_twoarg, args=(a, b))
        self.assertEqual(func_noargs(x),       func_noargs2(x, args=None))
        self.assertEqual(func_onearg(x, a),    func_onearg2(x, args=a))
        self.assertEqual(func_twoarg(x, a, b), func_twoarg2(x, args=(a, b)))


class TestGP(SeededTest):
    def test_func_args(self):
        X = np.linspace(0,1,10)[:,None]
        Y = np.random.randn(10,1)
        with Model() as model:
            # make a Gaussian model
            with self.assertRaises(ValueError):
                random_test = gp.GP('random_test', cov_func=gp.mean.Zero(), observed={'X':X, 'Y':Y})
            with self.assertRaises(ValueError):
                random_test = gp.GP('random_test', mean_func=gp.cov.Matern32(1, 1),
                                        cov_func=gp.cov.Matern32(1, 1), observed={'X':X, 'Y':Y})

    def test_sample(self):
        X = np.linspace(0,1,100)[:,None]
        Y = np.random.randn(100,1)
        with Model() as model:
            M = gp.mean.Zero()
            l = Uniform('l', 0, 5)
            K = gp.cov.Matern32(1, l)
            sigma = Uniform('sigma', 0, 10)
            # make a Gaussian model
            random_test = gp.GP('random_test', mean_func=M, cov_func=K, sigma=sigma, observed={'X':X, 'Y':Y})
            tr = sample(500, init=None, progressbar=False, random_seed=self.random_seed)
