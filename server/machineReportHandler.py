from pydantic import BaseModel, Field
from typing import List, Dict, Tuple
from utils import generateRandomString

class MachineReport(BaseModel):
    id: str = Field(default_factory=generateRandomString, alias="_id")
    targets: List[Tuple[str, str]] = Field(default_factory=lambda: [], description="Find the target as value pair")

class MachineReportHandler(MachineReport):
    def add_targets(self, target_or_targets: List[Tuple[str, str]]):
        self.targets.extend(target_or_targets)

    def does_targets_exist(self, nlp_output: dict) -> List[str]:
        found = []
        for unit, alias in self.targets:
            if any(p['unit'] == unit for p in self._get_unit_pair(nlp_output)):
                found.append(alias)
        return found

    @staticmethod
    def _get_unit_pair(nlp_output: dict) -> List[Dict[str, str]]:
        return nlp_output.get("unit_info", {}).get("unit_pairs", [])

    @staticmethod
    def _get_id_pair(nlp_output: dict) -> Dict[str, str]:
        ids_info = nlp_output.get('ids_info')
        if ids_info is None:
            raise ValueError('Cannot find ids_info')
        return ids_info

    def get_value(self, nlp_output: dict) -> List[str]:
        return [p['value'] for p in self._get_unit_pair(nlp_output)]

    def generate_machine_report(self, nlp_output: dict) -> Dict[str, Dict]:
        if "unit_info" not in nlp_output or "ids_info" not in nlp_output:
            raise ValueError("During the creation of machine-report, the data it needs cannot be found. If error persists, please add a feedback.")

        result = {}
        for unit, alias in self.targets:
            for pair in self._get_unit_pair(nlp_output):
                if pair["unit"] == unit:
                    result[alias] = pair
                    break

        ids_info = self._get_id_pair(nlp_output)
        result['machine_number'] = ids_info.get('id_matches') if ids_info.get('id_matches') else 'None'

        return result
