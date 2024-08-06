import json
import os
from intelli_suggetion import utils

class IntelliRule:
    rule_command = ""
    description = ""

    def __init__(self, name, rule_id):
        """
        Initializes an instance of IntelliRule with a given name.

        Parameters:
        - name (str): The name of the IntelliRule.
        - rule_id (str): The id of the IntelliRule.
        """
        self.name = name
        self.rule_id = rule_id
        

    def get_params(self, key: str):
        """
        Extracts and returns the components of a hierarchical key.

        Parameters:
        - key (str): The hierarchical key.

        Returns:
        - list or None: A list of components if key contains '.', otherwise None.
        """
        if '.' not in key:
            return None
        
        if "::" not in key:
            return key.split('.') + [None]
        
        if key.count('::') > 1:
            return ['error', 'Syntax error', 'More than one ::']
        
        part1, part2 = key.split('::')
        part1_split = part1.split('.')
        part2_float = part2

        if '.' not in part1:
            part1_split = [None] + part1_split
        
        return part1_split + [part2_float]


    def intelli(self, key: str, max_result: int):
        """
        Placeholder method for intelligent suggestions based on the key.

        Parameters:
        - key (str): The hierarchical key for which suggestions are needed.
        - max_result (int): The maximum number of suggestions to return.

        Returns:
        - list: A list of intelligent suggestions based on the key.
        """
        pass

    def complete(self, key: str):
        """
        Placeholder method for completing the given key.

        Parameters:
        - key (str): The hierarchical key to be completed.

        Returns:
        - str: The completed key.
        """
        pass

    def get_highlight(self, key: str) -> str:
        """
        Placeholder method for getting the highlight for the given key.

        Parameters:
        - key (str): The hierarchical key to be highlighted.

        Returns:
        - str: The highlighted key.
        """

        return "#FFFFFF"

    def remove_rule_name(self, key : str):
        """Remove the rule name from the key.

        Args:
            key (str): The hierarchical key to be remove.

        Returns:
            str: After remove key.
        """
        return key.removeprefix(self.rule_command + ".")

class KeywordIntelliRule(IntelliRule):
    """
    A rule class for intelligent keyword-based completion.

    Attributes:
    - keywords (list): A list to store keywords for intelligent completion.

    Methods:
    - __init__(self, name, rule_id): Initializes an instance of KeywordIntelliRule.
    - intelli(self, key, max_result): Performs intelligent completion based on keywords.
    - on_search(self, query, current_keyword, found, result): Callback function for search.
    - complete(self, key: str): Completes the provided key based on rule specifications.
    """

    keywords : list[str] = []

    def __init__(self, name, rule_id):
        """
        Initializes an instance of KeywordIntelliRule.

        Args:
        - name (str): The name of the rule.
        - rule_id (int): The unique identifier for the rule.
        """
        super().__init__(name, rule_id)

    def intelli(self, key : str, max_result : int):
        """
        Performs intelligent completion based on keywords.

        Args:
        - key (str): The input key for completion.
        - max_result (int): The maximum number of results to return.

        Returns:
        A list of completion results.
        """
        params = self.get_params(key)

        if params:
            

            result = []
            found = []
            query, strength = params[1], params[2]

            for keyword in self.keywords:

                found, result, skip = self.on_search(query, keyword, found, result)

                if skip == True:
                    continue

                if query == keyword:
                    found.insert(0, f"{self.rule_command}.{keyword}")
                    continue
                
                if keyword.startswith(query):
                    found.append(f"{self.rule_command}.{keyword}")
                    continue
                
                if utils.is_subsequence(query, keyword) == True:
                    result.append(f"{self.rule_command}.{keyword}")

            if strength:
                return [(f"{x}::{strength}", self.get_highlight(x)) for x in found + result][0:max_result]
            return [(x, self.get_highlight(x)) for x in found + result][0:max_result]

        return []

    def on_search(self, query : str, current_keyword : str, found : list, result : list) -> tuple[list, list, bool]:
        """
        Callback function. The function must return the tuple in the order found: list, result: list, skip: boolean.

        Args:
        - query (str): The search query.
        - current_keyword (str): The current keyword being processed.
        - found (list): The list of already found results.
        - result (list): The list of partial results.

        Returns:
        A tuple (found, result, skip).
        """
        return found, result, False

    def complete(self, key: str):
        """
        Completes the provided key based on rule specifications.

        Args:
        - key (str): The key to be completed.

        Returns:
        A completed string based on rule specifications.
        """
        key = self.remove_rule_name(key)

        if "::" in key:
            key, strength = key.split("::")

            return f"({key}:{strength}) "

        return f"{key} "

class MapKeywordIntelliRule(IntelliRule):
    """
    A rule class for intelligent keyword-based completion.
    This rule store the keyword with the count.
    Result will be sorted by the count.

    Attributes:
    - keywords (list): A list to store keywords for intelligent completion.

    """
    keywords : list[tuple[str, int]] = []
    def __init__(self, name, rule_id):
        """
        Initializes an instance of KeywordIntelliRule.

        Args:
        - name (str): The name of the rule.
        - rule_id (int): The unique identifier for the rule.
        """
        super().__init__(name, rule_id)

    def intelli(self, key : str, max_result : int):
        """
        Performs intelligent completion based on keywords.

        Args:
        - key (str): The input key for completion.
        - max_result (int): The maximum number of results to return.

        Returns:
        A list of completion results.
        """
        params = self.get_params(key)
        map_firts_found = []
        map_level_1 = []
        map_level_2 = []
        map_found = [] 
        if params:

            query, strength = params[1], params[2]
            
            for (keyword, count) in self.keywords:
                if query == keyword:
                    map_firts_found.append((f"{self.rule_command}.{keyword}", count))
                    continue
                
                if keyword.startswith(query):
                    # found.append(f"{self.rule_command}.{keyword}")
                    map_level_1.append((f"{self.rule_command}.{keyword}", count))
                    continue
                
                if query in keyword:
                    map_level_2.append((f"{self.rule_command}.{keyword}", count))
                    continue

                if utils.is_subsequence(query, keyword) == True:
                    # result.append(f"{self.rule_command}.{keyword}")
                    map_found.append((f"{self.rule_command}.{keyword}", count))

            map_found.sort(key=lambda x: x[1], reverse=True)
            map_level_1.sort(key=lambda x: x[1], reverse=True)
            map_level_2.sort(key=lambda x: x[1], reverse=True)
            map_firts_found.sort(key=lambda x: x[1], reverse=True)

            result_map = map_firts_found + map_level_1 + map_level_2 + map_found
            if strength:
                return [(f"{x[0]}::{strength}", self.get_highlight(x[0])) for x in result_map][0:max_result]
            return [(x[0], self.get_highlight(x[0])) for x in result_map][0:max_result]

        return []

    def complete(self, key: str):
        """
        Completes the provided key based on rule specifications.

        Args:
        - key (str): The key to be completed.

        Returns:
        A completed string based on rule specifications.
        """
        key = self.remove_rule_name(key)

        if "::" in key:
            key, strength = key.split("::")

            return f"({key}:{strength}) "

        return f"{key} "

RED_COLOR = "#FF0000"
PINK_COLOR = "#FF00FF"
GOLD = "#FFD700"
DEFAULT_RULE = "intelli_danbooru"

intelli_command_rules : dict[str, str] = {}
idx2intelli_rules : dict[str, IntelliRule] = {}
idx2intelli_rule_configs : dict[str, dict] = {}

def get_suggestion_rules(key: str, max_result: int):
    """
    Retrieves suggestion rules based on the given key and maximum number of results.

    Parameters:
    - key (str): The hierarchical key for which suggestions are needed.
    - max_result (int): The maximum number of suggestions to return.

    Returns:
    - list: A list of suggestion rules.
    """
    suggestion_rules = []
    if utils.check_syntax(key) != None:
        return [(utils.check_syntax(key), RED_COLOR)]
    
    if len(key) < 1:
        return list([(x, GOLD) for x in intelli_command_rules.keys()])[0:max_result]
    
    if not "." in key:
        for rule, rule_id in intelli_command_rules.items():
            if len(suggestion_rules) > max_result:
                break
            if utils.is_subsequence(key, rule) == True:
                suggestion_rules.append((rule, GOLD))

        if len(suggestion_rules)  < 1:
            rule = idx2intelli_rules[DEFAULT_RULE]
            suggestion_rules.extend(rule.intelli(f"{rule.rule_command}.{key}", max_result))

    else:
        for rule, rule_id in intelli_command_rules.items():
            if len(suggestion_rules) > max_result:
                break

            if key.split(".")[0] == rule:
                suggestion_rules.extend(idx2intelli_rules[rule_id].intelli(key, max_result))
                break
    
                
    if "::" in key and len(suggestion_rules) < 1:
        suggestion_rules.insert(0, (key, PINK_COLOR))

    return suggestion_rules

def get_suggestion_complete(key: str):
    """
    Retrieves the completion for the given key.

    Parameters:
    - key (str): The hierarchical key to be completed.

    Returns:
    - str: The completed key.
    """
    rule = key.split(".")[0]

    if not "." in key:
        return key
    
    if rule in intelli_command_rules:
        rule_id = intelli_command_rules[rule]
        return idx2intelli_rules[rule_id].complete(key)
    
    if "::" in key:
        tag, strength = key.split("::")

        return f"({tag.replace('_', ' ')}:{strength})"
    return key

def add_intelli_rules(key, rule: IntelliRule, short_keys=None):
    """
    Adds an IntelliRule to the global rule registry and associates it with a key.

    **Important**: Must be called after the module is loaded by stable-diffusion-webui, typically in `script_callbacks.on_before_ui()`.
    
    Parameters:
    - key (str): The key to associate with the IntelliRule.
    - rule (IntelliRule): The IntelliRule object to be added.
    - short_keys (list or None): Optional list of additional keys to associate with the same IntelliRule.

    Returns:
    None

    Modifies the global dictionaries:
    - idx2intelli_rules: Maps rule IDs to IntelliRule objects.
    - intelli_command_rules: Maps command keys to rule IDs.
    - idx2intelli_rule_configs: Maps rule IDs to configuration dictionaries.
    
    If short_keys are provided, they are also associated with the same IntelliRule.
    """

    # Set the rule command for the IntelliRule
    rule.rule_command = key

    # Add IntelliRule to the global registry
    idx2intelli_rules[rule.rule_id] = rule

    # Associate the key with the IntelliRule ID
    intelli_command_rules[key] = rule.rule_id

    # Add configuration if not already present
    if rule.rule_id not in idx2intelli_rule_configs:
        idx2intelli_rule_configs[rule.rule_id] = {}

    # Associate short keys with the same IntelliRule
    if short_keys:
        for short_key in short_keys:
            intelli_command_rules[short_key] = rule.rule_id


def get_intelli_rule_config(rule_id):
    """
    Get an IntelliRule config.

    Parameters:
    - rule_name (str): The name of IntelliRule.

    Returns:
    - dict : The IntelliRule config.
    """
    if not rule_id in idx2intelli_rule_configs:
        return None


    return idx2intelli_rule_configs[rule_id]

def set_intelli_rule_config(rule_id : str, config : dict):
    """
    Set an IntelliRule config.

    Parameters:
    - rule_id (str): The name of IntelliRule.
    - config (dict): The config of IntelliRule.

    Returns:
    - dict : The IntelliRule config.
    """
    if not rule_id in idx2intelli_rule_configs:
        return None

    idx2intelli_rule_configs[rule_id] = config

def create_defaut_intelli_rule_config(rule_id : str, config : dict):
    """
    Create an defaut IntelliRule config.

    Parameters:
    - rule_id (str): The name of IntelliRule.
    - config (dict): The config of IntelliRule.

    Returns:
    - dict : The IntelliRule config.
    """
    if not rule_id in idx2intelli_rule_configs:
        idx2intelli_rule_configs[rule_id] = {}

    config.update(idx2intelli_rule_configs[rule_id])
    idx2intelli_rule_configs[rule_id] = config

    return idx2intelli_rule_configs[rule_id]

def save_intelli_rule_configs(path : str):
    with open(path, 'w') as f:
        json.dump(idx2intelli_rule_configs, f, indent=4)


    