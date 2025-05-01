from pydantic import BaseModel, Field
from utils import *
from typing import List, Dict

from objects import MachineReport

class MachineReportHandler(MachineReport):
    def does_targets_exist(self) -> List[str]:
        found = []
        for unit, alias in self.targets:
            if any(p['unit'] == unit for p in self.nlp_output.get('unit_info', {}).get('unit_pairs', [])):
                found.append(alias)
        return found

    def get_unit_pair(self) -> List[Dict[str, str]]:
        return self.input.get("unit_info", {}).get("unit_pairs", [])

    def get_value(self) -> List[str]:
        return [p['value'] for p in self.get_unit_pair()]

    def generate_machine_report(self) -> Dict[str, Dict]:
        result = {}
        for unit, alias in self.targets:
            for pair in self.get_unit_pair():
                if pair["unit"] == unit:
                    result[alias] = pair
                    break
        
        result['machine_number'] = self.input['ids_info']['id_matches'] if self.input['ids_info']['id_matches'] else 'None' 
        self.output = result
        return result
    pass