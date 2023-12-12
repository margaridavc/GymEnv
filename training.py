import os
from sys import argv
from stable_baselines3 import A2C, DDPG, HER, PPO, SAC, TD3
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.a2c import MlpPolicy as A2C_MlpPolicy
from stable_baselines3.ddpg import MlpPolicy as DDPG_MlpPolicy
# from stable_baselines3.her import MlpPolicy as HER_MlpPolicy
from stable_baselines3.ppo import MlpPolicy as PPO_MlpPolicy
from stable_baselines3.sac import MlpPolicy as SAC_MlpPolicy
from stable_baselines3.td3 import MlpPolicy as TD3_MlpPolicy

from NewReward import RewardWrapper

env_id = "CarRacing-v2"
TIMESTEPS = 100000
models_dir = "models"
logdir = "logs"
NUM_ENVS = os.cpu_count()


def latest_model(algorithm):
    models = [int(model.split(".")[0]) for model in os.listdir(f"{models_dir}/{algorithm}")]
    models.sort()
    return f"{models_dir}/{algorithm}/{models[-1]}.zip"


def train_model(algo, algo_name, policy, env):
    if os.path.exists(f"{models_dir}/{algo_name}"):
        if os.listdir(f"{models_dir}/{algo_name}"):
            model_path = latest_model(algo_name)
            model = algo.load(model_path, env=env)
            iters = int(int(model_path.split("/")[2].split(".")[0]) / 10 ** 4)
        else:

            # policy_kwargs=dict(net_arch=[{"conv1d": [32, 3, 1]}, {"fc": [256]}])  CNN nn architecture

            model = algo(policy, env, verbose=1,
                         tensorboard_log=logdir)  # (hyperparameter) ,learning_rate=0.0001, (Neural Network Architecture change)(Neural Network Architecture change) policy_kwargs=dict(net_arch=[256,(...n_layers...), 256]))
            iters = 0
    else:
        os.makedirs(f"{models_dir}/{algo_name}")
        model = algo(policy, env, verbose=1,
                     tensorboard_log=logdir)  # (hyperparameter) ,learning_rate=0.0001, (Neural Network Architecture change) policy_kwargs=dict(net_arch=[256,(...n_layers...), 256])
        iters = 0

    while True:
        iters += 1
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False,
                    tb_log_name=algo_name)  # (hyperparameters) , batch_size=256, ent_coef=0.01, vf_coef=0.5, gae_lambda=0.95))
        model.save(f"{models_dir}/{algo_name}/{TIMESTEPS * iters}")


def main():
    try:
        if len(argv) != 2:
            raise ValueError("No arguments given. Please specify which model to train.")

        if not os.path.exists(logdir):
            os.makedirs(logdir)

        model_type = argv[1]

        # Create the vectorized environment using make_vec_env and the new wrapper: RewardWrapper
        env = make_vec_env(env_id, n_envs=NUM_ENVS, vec_env_cls=SubprocVecEnv,
                           vec_env_kwargs=dict(start_method='fork'))

        if model_type == "A2C":
            train_model(A2C, model_type, A2C_MlpPolicy, env)
        elif model_type == "DDPG":
            train_model(DDPG, model_type, DDPG_MlpPolicy, env)
        # elif model_type == "HER":
            # train_model(HER, model_type, HER_MlpPolicy, env)
        elif model_type == "PPO":
            train_model(PPO, model_type, PPO_MlpPolicy, env)
        elif model_type == "SAC":
            train_model(SAC, model_type, SAC_MlpPolicy, env)
        elif model_type == "TD3":
            train_model(TD3, model_type, TD3_MlpPolicy, env)
        else:
            raise ValueError("Invalid argument. Please specify a valid algorithm.")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
