from role.Role import Role
from typing import Dict, List, Set, TYPE_CHECKING


class DirectoryFacilitator:
    def __init__(self):
        self.df_: Dict[Role, List] = dict()

    def add_role(self, role: Role):
        """
        Add a specific role in df_
        """
        self.df_[role] = []

    def attach_a_role_to_agent(self, role: Role, agent_id: str):
        """
        Permits to indicate that a specific agent can achieve a specific role.
        """
        self.df_[role].append(agent_id)

    def get_agents_with_specific_role(self, requester_name: str, role: Role) -> Set[str]:
        """
        Return a list of agents with a specific role.
        """
        return set([agent_id for agent_id in self.df_[role] if agent_id != requester_name])


if __name__ == '__main__':
    df = DirectoryFacilitator()

    # Check to add a role
    df.add_role(Role.EnginesTalker)

    assert len(list(df.df_.keys())) == 1
    print("[INFO] Testing method to add role... OK")

    # Checking method to return agents with specific roles
    agents = df.get_agents_with_specific_role('', Role.EnginesTalker)

    assert len(agents) == 0
    print("[INFO] Method get_agents_with_specific_role should return  0 agent... OK ")

    # Test to add a role to a specific agent
    agent_1 = "AgentSmith"
    agent_2 = "AgentPamela"

    df.attach_a_role_to_agent(Role.EnginesTalker, agent_1)
    df.attach_a_role_to_agent(Role.EnginesTalker, agent_2)

    interlocutors = df.get_agents_with_specific_role('', Role.EnginesTalker)

    assert len(interlocutors) == 2
    print("[INFO] Method get_agents_with_specific_role should return 2 agents... OK")

    interlocutors = df.get_agents_with_specific_role(agent_1, Role.EnginesTalker)

    assert len(interlocutors) == 1
    assert list(interlocutors)[0] == agent_2
    print("[INFO] Method get_agents_with_specific_role should return 2 agents... OK")
