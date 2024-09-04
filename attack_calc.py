import math
import random as rand


def calc_effective_level(
    base_level: int,
    boost: int,
    prayer: float,
    style: str,
    stance_bonus: int = 0,
    void: bool = False,
) -> int:
    """Calcuate a player's effective melee strength level

    Args:
        base_level (int): Non boosted strength stat, from 1 to 99
        boost (int): additional boost caused by potion, overload, smelling salts, etc
        prayer (float): a postive multiplier from the strength-boosting offensive prayers like Piety
        style: what combat stat you are calculating for (attack,strength,defence,ranged,magic)
        stance_bonus (int, optional): combat stance in-game, typically +3 if stance is aggressive. Defaults to 0
        void (bool, optional): Whether the player is wearing Void Melee. Defaults to False.

    Returns:
        int: An effective melee strength level
    """
    effective_level = (base_level + boost) * prayer
    effective_level = math.floor(effective_level)
    effective_level += stance_bonus
    effective_level += 8
    if void and style.lower() != 'mage' and style.lower() != 'defence':
        effective_level *= 1.1
    elif style.lower() == 'mage':
        effective_level *= 1.45

    effective_level = math.floor(effective_level)
    return effective_level



def calc_max_hit(
    effective_level: int, equipment_bonus: int, target_bonus: float = 1.0
) -> int:
    """Calculates the maximum rollable hit
    Args:
        effective_strength_level (int): effective strength or ranged level stat
        equipment_bonus (int): strength bonus shown on equipment screen
        target_bonus (float, optional): multiplier for damage buffs like slayer helmet or salve amulet. Defaults to 1.0.

    Returns:
        int: Maximum rollable melee damage for selected gear and stats
    """
    max_hit = effective_level * (equipment_bonus + 64)
    max_hit += 320
    max_hit = math.floor(max_hit / 640)
    max_hit = math.floor(max_hit * target_bonus)
    return max_hit



def calc_max_attack_roll(
    effective_attack_level: int, equipment_bonus: int, target_bonus: float = 1.0
) -> int:
    """Calculates an attack's maximum possible accuracy roll

    Args:
        effective_attack_level (int): This is the acccuracy level for melee, range, and magic
        equipment_bonus (int): attack bonus shown on equipmeent screen
        target_bonus (float, optional): multiplier for accuracy buffs like demonbane or dragonbane. Defaults to 1.0.

    Returns:
        int: maximum accuracy roll
    """
    attack_roll = effective_attack_level * (equipment_bonus + 64)
    attack_roll *= target_bonus
    attack_roll = math.floor(attack_roll)
    if attack_roll < 0:
        attack_roll = 0
    return attack_roll


def calc_npc_max_defence_roll(base_level: int, style_bonus: int) -> int:
    """Calculate an NPC's maximum defence roll

    Args:
        base_level (int): The NPC's base defence level
        style_bonus (int): The style-specific defence stat you are attack against (ie crush, range, stab etc)

    Returns:
        int: NPC's maximum defence roll
    """
    defence_roll = (base_level + 9) * (style_bonus + 64)
    if defence_roll < 0:
        defence_roll = 0
    return defence_roll


def calc_player_max_defence_roll(
    effective_defence_level: int, equipment_bonus: int
) -> int:
    """Calculate a player's maximum defence roll

    Args:
        effective_defence_level (int): the player's pre-calculated effective defence
        equipment_bonus (int): style-specific defence value shown on the equipment screen

    Returns:
        int: Player's maximum defence roll against non-magic attacks (melee, range)
    """
    defence_roll = effective_defence_level * (equipment_bonus + 64)
    if defence_roll < 0:
        defence_roll = 0
    return defence_roll


def calc_player_max_magic_defence_roll(
    magic_level: int,
    magic_boost: int,
    effective_defence_level: int,
    equipment_bonus: int,
    prayer: float = 1.0,
) -> int:
    """Calculates a player's maximum defence roll when attacked with magic

    Args:
        magic_level (int): Non boosted magic stat, from 1 to 99
        magic_boost (int): additional boost caused by imbued heart, overload, smelling salts, etc
        effective_defence_level (int): the player's pre-calculated effective defence
        equipment_bonus (int): magic defence stat found on the equipment screen
        prayer (float, optional): a postive multiplier from the magic prayers like Augury

    Returns:
        int: Player's maximum defence roll against magic attacks
    """
    effective_defence_level = math.floor(effective_defence_level * 0.3)

    magic_level = (magic_level + magic_boost) * prayer
    magic_level = math.floor(magic_level)
    effective_magic_level = math.floor(magic_level * 0.7)

    effective_level = effective_magic_level + effective_defence_level

    magic_defence_roll = effective_level * (equipment_bonus + 64)

    if magic_defence_roll < 0:
        magic_defence_roll = 0

    return magic_defence_roll


def roll_attack(max_attack_roll: int, max_defence_roll: int) -> bool:
    """Randomly rolls an attack against a defence for a chance of a hit

    Args:
        max_attack_roll (int): an attack's non-negative maximum attack roll
        max_defence_roll (int): a defender's non-negative maximum defence roll

    Returns:
        bool: whether the attack landed or not
    """
    attack_roll = rand.randrange(max_attack_roll)
    defence_roll = rand.randrange(max_defence_roll)

    return attack_roll > defence_roll


def calc_hit_chance(max_attack_roll: int, max_defence_roll: int) -> float:
    """Calculates the chances of an attack landing against a defence

    Args:
        max_attack_roll (int): an attack's non-negative maximum attack roll
        max_defence_roll (int): a defender's non-negative maximum defence roll

    Returns:
        float: a probability of an attack hitting, between 0 and 1
    """
    if max_attack_roll > max_defence_roll:
        return 1 - ((max_defence_roll + 2) / (2 * (max_attack_roll + 1)))
    else:
        return max_attack_roll / (2 * (max_defence_roll + 1))


def roll_hit_damage_normal(max_hit: int) -> int:
    """random rolls a number between 0 and max_hit

    Args:
        max_hit (int): the max hit to roll

    Returns:
        int: a number between - and max_hit
    """
    return rand.randrange(max_hit)
