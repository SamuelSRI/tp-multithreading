import unittest
import numpy as np
import numpy.testing as npt

from task import Task


class TestTask(unittest.TestCase):
    def test_init_default(self):
        """Vérifie que le constructeur initialise bien les attributs de base."""
        t = Task()

        self.assertEqual(t.identifier, 0)
        self.assertIsInstance(t.size, int)
        self.assertGreaterEqual(t.size, 300)
        self.assertLessEqual(t.size, 3000)

        self.assertEqual(t.a.shape, (t.size, t.size))
        self.assertEqual(t.b.shape, (t.size,))
        self.assertEqual(t.x.shape, (t.size,))

    def test_init_with_size_and_id(self):
        """Vérifie qu'on peut fixer la taille et l'identifiant."""
        size = 10
        identifier = 42
        t = Task(identifier=identifier, size=size)

        self.assertEqual(t.identifier, identifier)
        self.assertEqual(t.size, size)
        self.assertEqual(t.a.shape, (size, size))
        self.assertEqual(t.b.shape, (size,))
        self.assertEqual(t.x.shape, (size,))

    def test_work_computes_solution_and_time(self):
        """Vérifie que work() calcule bien x et mesure un temps > 0."""
        size = 10  # petite taille pour la vitesse des tests
        t = Task(size=size)

        # avant work : x doit être nul et time = 0
        npt.assert_allclose(t.x, np.zeros(size))
        self.assertEqual(t.time, 0)

        # exécution du travail
        t.work()

        # après work : x doit avoir changé
        self.assertFalse(np.allclose(t.x, np.zeros(size)))

        # le temps doit être strictement positif
        self.assertGreater(t.time, 0)

        # vérification mathématique : A·x ≈ b
        Ax = t.a @ t.x
        npt.assert_allclose(Ax, t.b, rtol=1e-6, atol=1e-6)


if __name__ == "__main__":
    unittest.main()
