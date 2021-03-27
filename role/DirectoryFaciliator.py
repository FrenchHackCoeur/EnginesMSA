from role.Role import Role
from typing import Dict, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from pw_argumentation import ArgumentAgent


class DirectoryFacilitator:
    def __init__(self):
        self.df_: Dict[str, List] = dict()

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

    def get_agents_with_specific_role(self, requester: 'ArgumentAgent', role: Role) -> Set[str]:
        """
        Return a list of agents with a specific role.
        """
        return set([agent_id for agent_id in self.df_[role] if agent_id != requester.get_name()])
