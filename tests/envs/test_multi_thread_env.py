import unittest
import gym
import numpy as np
import tensorflow as tf

from tf2rl.envs.multi_thread_env import MultiThreadEnv


class TestMultiThreadEnv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch_size = 64
        cls.thread_pool = 4
        cls.max_episode_steps = 1000
        env_fn = lambda: gym.make("Pendulum-v0")
        cls.continuous_sample_env = env_fn()
        cls.continuous_envs = MultiThreadEnv(
            env_fn=env_fn,
            batch_size=cls.batch_size,
            max_episode_steps=cls.max_episode_steps)
        env_fn = lambda: gym.make("CartPole-v0")
        cls.discrete_sample_env = env_fn()
        cls.discrete_envs = MultiThreadEnv(
            env_fn=env_fn,
            batch_size=cls.batch_size,
            max_episode_steps=cls.max_episode_steps)

    def test_py_reset(self):
        obses = self.continuous_envs.py_reset()
        self.assertEqual(self.batch_size, obses.shape[0])
        self.assertEqual(self.continuous_sample_env.observation_space.low.size, obses.shape[1])
        obses = self.discrete_envs.py_reset()
        self.assertEqual(self.batch_size, obses.shape[0])
        self.assertEqual(self.discrete_sample_env.observation_space.low.size, obses.shape[1])

    def test_step(self):
        actions = [self.continuous_sample_env.action_space.sample()
                   for _ in range(self.batch_size)]
        actions = tf.convert_to_tensor(actions)
        obses, rewards, dones, _ = self.continuous_envs.step(actions)
        self.assertEqual(self.batch_size, obses.shape[0])
        self.assertEqual(self.batch_size, rewards.shape[0])
        self.assertEqual(self.batch_size, dones.shape[0])

        for _ in range(self.continuous_envs.max_episode_steps - 2):
            obses, rewards, dones, _ = self.continuous_envs.step(actions)
        np.testing.assert_array_equal(dones, np.zeros_like(dones))
        obses, rewards, dones, _ = self.continuous_envs.step(actions)
        np.testing.assert_array_equal(dones, np.ones_like(dones))

        actions = [self.discrete_sample_env.action_space.sample()
                   for _ in range(self.batch_size)]
        actions = tf.convert_to_tensor(actions)
        obses, rewards, dones, _ = self.discrete_envs.step(actions)
        self.assertEqual(self.batch_size, obses.shape[0])
        self.assertEqual(self.batch_size, rewards.shape[0])
        self.assertEqual(self.batch_size, dones.shape[0])


if __name__ == '__main__':
    config = tf.ConfigProto(allow_soft_placement=True)
    tf.enable_eager_execution(config=config)
    unittest.main()
