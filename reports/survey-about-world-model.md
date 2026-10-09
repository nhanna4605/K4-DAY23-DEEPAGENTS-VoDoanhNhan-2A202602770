# Survey on World Models

## TL;DR
- World models are internal predictive models that capture environment dynamics, enabling prediction, planning, and reasoning [1].
- Model-based reinforcement learning leverages various architectures such as VQ-VAE with ConvLSTM, stochastic transformers, and state-space models to improve sample efficiency and performance [2][3][4].
- Applications in robotics include vision-language-action models trained on large real-world datasets, geometry-enhanced video models for manipulation, and generative simulators for policy evaluation [5][6][7][8].
- Recent advances focus on integrating language and multimodal inputs, improving long-horizon reasoning, and addressing challenges like sim-to-real transfer and safety [9][10][11].

## Background
World models are internal simulators that learn the structure and dynamics of an environment, allowing agents to predict future states, plan actions, and reason about outcomes [1]. They are defined as internal predictive models capturing how an environment evolves over time and how this evolution depends on an agent's actions. The objective is to learn state representations that make future outcomes predictable rather than reproducing the external world in full detail. World models can be categorized by observation-space vs latent-space, deterministic vs stochastic, and task-specific vs general-purpose models. They often operate within a partially observable Markov decision process (POMDP) framework [1].

## Model-Based Reinforcement Learning Architectures
Model-based reinforcement learning (MBRL) uses world models to simulate environment dynamics and generate training data for policy learning. Various architectures have been proposed:

- VQ-VAE with ConvLSTM encodes observations into discrete latent embeddings and predicts future embeddings, enabling sample-efficient training with limited real environment interactions [2].
- STORM employs stochastic transformers to model sequence dynamics with self-supervised learning, enhancing the model's generative capabilities [3].
- State-space world models focus on compact latent representations of environment states, reducing the need for extensive environment interactions and improving robot learning [4].

These approaches differ in their representation of state, handling of uncertainty, and training methods. Performance comparisons highlight trade-offs between sample efficiency, model complexity, and generalization to diverse tasks [2][3][4].

## Applications in Robotics and Control
World models have been successfully applied in robotics and control tasks:

- Vision-language-action models trained on over 100k hours of real-world trajectories enable robots to follow diverse language instructions and adapt to novel tasks with minimal fine-tuning [5].
- Generative world models simulate realistic observations and interactions for scalable policy evaluation, including out-of-distribution scenarios [6].
- Geometry-enhanced video world models improve physical grounding for reliable robot manipulation by leveraging dense 4D correspondence supervision [7].
- Neural network simulators with dual-autoregressive mechanisms support robust policy optimization in robotics, enhancing real-world control [8].

These applications demonstrate the integration of semantic understanding, physical dynamics, and policy learning within world models to address complex robotic tasks [5][6][7][8].

## Recent Advances
Recent research has advanced the taxonomy, benchmarks, and capabilities of world models:

- Integration of language and multimodal inputs enhances world model reasoning and planning abilities [9][11].
- Dual Preference Optimization improves embodied task planning by jointly optimizing state prediction and action selection [10].
- Challenges remain in long-horizon reasoning due to error accumulation, underdeveloped action conditioning, and difficulties in sim-to-real transfer [9].
- Data scarcity and safety concerns are critical issues for deploying world models in real-world applications [9].
- Novel approaches explore large language model agents simulating physical dynamics and adding real-time spatial sound to world models [12][13].

These trends highlight the ongoing efforts to improve world model robustness, generalization, and applicability across domains [9][10][11].

## Trends and open problems
The field of world models is rapidly evolving with several key trends and open problems:

- The taxonomy of world models is becoming more structured, covering diverse architectures and application domains [9].
- Recent advances focus on combining semantic understanding with physical dynamics, especially in robotics [11].
- Long-horizon reasoning remains a significant challenge due to error accumulation and state instability [9].
- Action conditioning in world models is underdeveloped, limiting their ability to plan complex sequences of actions [9].
- Sim-to-real transfer is difficult because of noise, sensor differences, and physical complexity in real environments [9].
- Data bottlenecks persist as video, action, and trajectory data are expensive and scarce [9].
- Safety and uncertainty estimation are crucial for deploying world models in safety-critical applications like robotics and autonomous driving [9].

Addressing these challenges is essential for advancing the practical utility and reliability of world models in diverse AI systems.

## References
[1] World Models: A Comprehensive Survey of Architectures, Methodologies, Reasoning Paradigms, and Applications. arxiv. https://arxiv.org/abs/2606.00133 (2026-05-28)
[2] Smaller World Models for Reinforcement Learning. arxiv. https://arxiv.org/abs/2010.05767 (2020-10-12)
[3] STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning. arxiv. https://arxiv.org/abs/2310.09615 (2023-10-14)
[4] Accelerating Model-Based Reinforcement Learning with State-Space World Models. arxiv. https://arxiv.org/abs/2502.20168 (2025-02-27)
[5] Xiaomi-Robotics-1: Scaling Vision-Language-Action Models with over 100K Hours of Real-World Trajectories. arxiv. https://arxiv.org/abs/2607.15330 (2026-07-16)
[6] Evaluating Gemini Robotics Policies in a Veo World Simulator. arxiv. https://arxiv.org/abs/2512.10675 (2025-12-11)
[7] GEM-4D: Geometry-Enhanced Video World Models for Robot Manipulation. arxiv. https://arxiv.org/abs/2605.22882 (2026-05-20)
[8] Robotic World Model: A Neural Network Simulator for Robust Policy Optimization in Robotics. hf-search. https://huggingface.co/papers/2501.10100 (2025-01-17)
[9] State of World Models 2026: Taxonomy, Benchmarks and Open Challenges. web. https://world-models.io/reports/state-of-world-models-2026/state-of-world-models-2026-v1.0.pdf (n.d.)
[10] World Modeling Makes a Better Planner: Dual Preference Optimization for Embodied Task Planning. hf-search. https://huggingface.co/papers/2503.10480 (2025-03-13)
[11] Rewiring Semantics, Dynamics, and Control: A Simple yet Effective Action-Centric Tri-Stream Transformer. arxiv. https://arxiv.org/abs/2610.11416 (2026-10-08)
[12] WorldSolver: Can LLM Agents Simulate the Physical Dynamics via Solver Generation?. arxiv. https://arxiv.org/abs/2610.08720 (2026-10-06)
[13] WorldSonus: Bringing Sound to Worlds. arxiv. https://arxiv.org/abs/2610.08760 (2026-10-06)
