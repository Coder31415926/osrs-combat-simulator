import attack_calc as ac
from abc import ABC, abstractmethod
from typing import List, Union
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class CombatStats:
    hitpoints: int
    strength: int
    attack: int
    defence: int
    range: int
    magic: int


@dataclass
class MonsterAggressiveStats:
    melee_attack_bonus: int
    melee_strength_bonus: int
    magic_attack_bonus: int
    magic_strength_bonus: int
    range_attack_bonus: int
    range_strength_bonus: int


@dataclass
class MonsterDefensiveStats:
    stab_defence_bonus: int
    slash_defence_bonus: int
    crush_defence_bonus: int
    magic_defence_bonus: int
    range_defence_bonus: int


@dataclass
class MonsterCombatInfo:
    size: int
    combat_level: int
    monster_attributes: list
    slayer_category: Union[None, str, list]
    attack_style: list
    attack_speed: Union[int, list]
    poisonous: bool


@dataclass
class MonsterImmunities:
    immune_to_poison: Union[bool, None]
    immune_to_venom: Union[bool, None]


@dataclass
class MonsterMetadata:
    examine: Union[list, str, None]
    category: Union[list, str, None]
    npc_id: Union[list, int]


class Character(ABC):
    @abstractmethod
    def __init__(self, combat_stats: CombatStats):
        self.combat_stats = combat_stats

    @abstractmethod
    def attempt_attack(self, target: "Character"):
        pass

    @abstractmethod
    def take_damage(self, damage: int):
        pass

    @abstractmethod
    def die(self):
        pass


class Player(Character):
    def __init__(self, combat_stats: CombatStats):
        self.combat_stats = combat_stats

        self.stab_bonus: int = 0
        self.slash_bonus: int = 0
        self.crush_bonus: int = 0
        self.strength_bonus: int = 0
        self.magic_attack_bonus: int = 0
        self.magic_strength_bonus: int = 0
        self.range_attack_bonus: int = 0
        self.range_strength_bonus: int = 0

        self.stab_defence: int = 0
        self.slash_defence: int = 0
        self.crush_defence: int = 0
        self.magic_defence: int = 0
        self.range_defence: int = 0

        self.boost: int = 0

        self.effective_melee_attack: int
        self.effective_melee_strength: int
        self.effective_magic_attack: int

        self.poison_immune: bool = False

        self.attack_timer: int = 0
        self.eat_timer: int = 0
        self.pot_timer: int = 0
        self.karam_timer: int = 0

        self.attack_speed: int = 4

    def get_effective_melee_strength(self):
        eff_str = ac.calc_effective_level(
            self.combat_stats.strength, self.boost, 1.0, 'melee', 3
        )
        self.effective_melee_strength = eff_str

    def get_effective_melee_attack(self):
        eff_atk = ac.calc_effective_level(
            self.combat_stats.attack, self.boost, 1.0, 'melee', 0
        )

        self.effective_melee_attack = eff_atk

    def attempt_attack(self, enemy: "Monster"):
        self.get_effective_melee_attack()
        self.get_effective_melee_strength()

        max_hit = ac.calc_max_hit(self.effective_melee_strength, 0)
        max_attack_roll = ac.calc_max_attack_roll(self.effective_melee_attack, 0)
        enemy_max_defence_roll = ac.calc_npc_max_defence_roll(
            enemy.combat_stats.defence, enemy.defensive_stat.crush_defence_bonus
        )

        hit = ac.roll_attack(max_attack_roll, enemy_max_defence_roll)
        if hit:
            hit_damage = ac.roll_hit_damage_normal(max_hit)
            print(f"Attack hits, dealing {hit_damage} to {enemy.name}")
            enemy.take_damage(hit_damage)
        else:
            print(f"Attack missed!")

    def take_damage(self, damage_value):
        self.combat_stats.hitpoints -= damage_value

    def die(self):
        print(f"Player has died")


class Monster(Character):
    def __init__(
        self,
        name: str,
        combat_stats: CombatStats,
        aggressive_stats: MonsterAggressiveStats,
        defensive_stats: MonsterDefensiveStats,
        combat_info: MonsterCombatInfo,
        immunities: MonsterImmunities,
        metadata: MonsterMetadata,
    ):
        self.name = name
        self.combat_stats = combat_stats
        self.aggressive_stats = aggressive_stats
        self.defensive_stat = defensive_stats
        self.combat_info = combat_info
        self.immunities = immunities
        self.metadata = metadata

    def attempt_attack(self, target: Character):

        pass

    def take_damage(self, damage_value):
        self.combat_stats.hitpoints -= damage_value
        if self.combat_stats.hitpoints <= 0:
            self.die()
            print(
                f"{self.name} takes {abs(max(damage_value, self.combat_stats.hitpoints))} damage, leaving its health at {self.combat_stats.hitpoints}"
            )
            print(f"{self.name} has died")

        else:
            print(
                f"{self.name} takes {damage_value} damage, leaving its health at {self.combat_stats.hitpoints}"
            )

    def die(self):
        self.combat_stats.hitpoints = 0


def search_and_construct_monster(monster_string: str):
    base_path = Path(__file__).resolve().parent
    monsters_path = base_path / "data" / "monster_stats.json"
    monsters_stats = json.loads(monsters_path.read_text())

    monster_search_result = monsters_stats.get(monster_string)
    if monster_search_result:
        m_combat_stats = monster_search_result.get("combat_stats")
        m_aggressive_stats = monster_search_result.get("aggressive_stats")
        m_defensive_stats = monster_search_result.get("defensive_stats")
        m_combat_info = monster_search_result.get("combat_info")
        m_immunities = monster_search_result.get("immunities")
        m_metadata = monster_search_result.get("metadata")

        combat_stats_class = CombatStats(**m_combat_stats)
        aggressive_stats_class = MonsterAggressiveStats(**m_aggressive_stats)
        defensive_stats_class = MonsterDefensiveStats(**m_defensive_stats)
        combat_info_class = MonsterCombatInfo(**m_combat_info)
        immunities_class = MonsterImmunities(**m_immunities)
        metadata_class = MonsterMetadata(**m_metadata)

        monster_class = Monster(
            name=monster_string,
            combat_stats=combat_stats_class,
            aggressive_stats=aggressive_stats_class,
            defensive_stats=defensive_stats_class,
            combat_info=combat_info_class,
            immunities=immunities_class,
            metadata=metadata_class,
        )

        print(f"{monster_class.name} found! {monster_class.combat_stats}")
        return monster_class
    else:
        print("Could not find or construct class from json data")
        return None


if __name__ == "__main__":
    ticks_to_kill = []
    for _ in range(100):
        counter = 0
        crab = search_and_construct_monster("Ammonite Crab")
        player = Player(
            CombatStats(
                hitpoints=99, strength=99, attack=99, defence=99, range=99, magic=99
            )
        )
        while crab.combat_stats.hitpoints > 0:
            player.attempt_attack(crab)
            counter += player.attack_speed
        counter -= player.attack_speed
        ticks_to_kill.append(counter)

    average_ttk = (sum(ticks_to_kill) / len(ticks_to_kill)) * 0.6
    print(average_ttk)
