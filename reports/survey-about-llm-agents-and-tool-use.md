# Survey on LLM Agents and Tool Use

## TL;DR
- LLM agents have evolved from passive text generators to autonomous systems capable of planning, tool use, and multi-agent collaboration [1].
- Architectures for LLM agents include design patterns like MLAT and frameworks such as AgentForge and Orchestral AI, enabling modular and scalable integration of tools [2][3][4].
- Real-world applications span e-commerce, finance, software development, education, and hiring, with companies like Instacart and GitHub deploying LLM-powered assistants and copilots [5].
- Recent trends emphasize multi-tool orchestration, personalization, and security challenges, with ongoing research on evaluation frameworks and secure agentic AI [6][7][8].

## Background
Large Language Model (LLM) agents represent a paradigm shift from passive text generation to autonomous decision-making entities capable of interacting with external tools, planning multi-step tasks, and collaborating in multi-agent systems [1][9]. This evolution is driven by advances in reinforcement learning, retrieval-augmented generation (RAG), and feedback learning, which enable LLMs to extend their capabilities beyond static text generation [10]. Foundational surveys highlight the importance of evidence tracing and execution provenance to understand and verify agent behavior, as well as the need for unified taxonomies and evaluation frameworks to systematically analyze LLM agents [1][11]. Personalized LLM-powered agents adapt to individual users, maintaining continuity and enhancing effectiveness across interactions [12].

## Architectures and Frameworks for LLM Agents Using Tools
Architectural designs for LLM agents focus on modularity, scalability, and effective tool integration. The Machine Learning as a Tool (MLAT) pattern treats pre-trained ML models as callable tools within LLM workflows, allowing dynamic invocation based on context [2]. The Control Plane as a Tool design pattern addresses orchestration, safety, and extensibility challenges in agentic AI systems [13]. Frameworks like AgentForge and Orchestral AI provide lightweight, modular platforms for building and orchestrating LLM agents across providers, emphasizing unified interfaces and reproducibility [3][4]. Multi-agent systems benefit from unified communication protocols that reduce inference costs and ambiguity, improving coordination [14]. Studies reveal significant performance variations in multi-agent frameworks due to architectural choices, highlighting trade-offs between latency and accuracy [15].

## Applications and Use Cases of LLM Agents with Tool Use
LLM agents have been widely adopted across industries. In e-commerce, Instacart's AI assistant Ava supports coding and internal tool development, while Wayfair's Agent Co-pilot aids digital sales agents with live chat responses [5]. Financial institutions like the Royal Bank of Canada use RAG-based systems to navigate internal policies [5]. Software development benefits from tools like GitHub Copilot, which offers AI-powered code suggestions [5]. Educational applications include AI faculty chatbots such as ChatLTV [5]. Hiring processes are streamlined by conversational AI assistants like Upwork's Uma and LinkedIn's Hiring Assistant [5]. These applications demonstrate the versatility and impact of LLM agents in automating complex tasks and enhancing productivity.

## Evaluation and Benchmarking of LLM Agents
Evaluation of LLM agents has become increasingly important to measure their capabilities and real-world effectiveness. Surveys propose two-stage evaluation frameworks that assess core LLM abilities and agent-specific capabilities [11]. Benchmarks like GTA focus on general tool agents, emphasizing real user queries and multi-step tasks to better reflect practical problem-solving [15]. Evaluation challenges include variability in LLM-based assessments and the need for benchmarks that capture multi-modal interactions and long-term agent behavior [11][15].

## Trends and Open Problems
Recent research highlights the evolution from single-tool calls to complex multi-tool orchestration, addressing challenges in managing long trajectories, intermediate states, and execution feedback [6]. Personalization remains a critical area, with agents adapting to user preferences and maintaining interaction continuity [12]. Security concerns have grown with increased agent autonomy, encompassing threats to the agents themselves and their use in cybersecurity offense and defense [8][8]. Evaluation frameworks are evolving to better capture agent capabilities, with benchmarks like GTA emphasizing real-world problem-solving and multi-modal interactions [11][15]. Open problems include secure agentic AI, lifecycle alignment, and translating research advances into productive industry applications [7][10].

## References
[1] From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents. arxiv. https://arxiv.org/abs/2606.04990 (2026-06-03)
[2] Machine Learning as a Tool (MLAT): A Framework for Integrating Statistical ML Models as Callable Tools within LLM Agent Workflows. arxiv. https://arxiv.org/abs/2602.14295 (2026-02-15)
[3] Orchestral AI: A Framework for Agent Orchestration. hf-search. https://huggingface.co/papers/2601.02577 (2026-01-05)
[4] A Lightweight Modular Framework for Constructing Autonomous Agents Driven by Large Language Models: Design, Implementation, and Applications in AgentForge. hf-search. https://huggingface.co/papers/2601.13383 (2026-01-19)
[5] 55 real-world LLM applications and use cases from top companies. web. https://www.evidentlyai.com/blog/llm-applications (2024-07-15)
[6] The Evolution of Tool Use in LLM Agents: From Single-Tool Call to Multi-Tool Orchestration. arxiv. https://arxiv.org/abs/2603.22862 (2026-03-24)
[7] LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions. arxiv. https://arxiv.org/abs/2510.04023 (2025-10-05)
[8] LLM agents security duality: a comprehensive survey of self-security and empowered cybersecurity. arxiv. https://arxiv.org/abs/2606.28450 (2026-06-26)
[9] Understanding Multi-Agent LLM Frameworks: A Unified Benchmark and Experimental Analysis. hf-search. https://huggingface.co/papers/2602.03128 (2026-02-03)
[10] Empowering Real-World: A Survey on the Technology, Practice, and Evaluation of LLM-driven Industry Agents. arxiv. https://arxiv.org/abs/2510.17491 (2025-10-20)
[11] The Landscape of Agentic Reinforcement Learning for LLMs: A Survey. arxiv. https://arxiv.org/abs/2509.02547 (2025-09-02)
[12] A Survey of Useful LLM Evaluation. arxiv. https://arxiv.org/abs/2406.00936 (2024-06-03)
[13] Control Plane as a Tool: A Scalable Design Pattern for Agentic AI Systems. hf-search. https://huggingface.co/papers/2505.06817 (2025-05-11)
[14] From Secure Agentic AI to Secure Agentic Web: Challenges, Threats, and Future Directions. arxiv. https://arxiv.org/abs/2603.01564 (2026-03-02)
[15] GTA: A Benchmark for General Tool Agents. arxiv. https://arxiv.org/abs/2407.08713 (2024-07-11)
