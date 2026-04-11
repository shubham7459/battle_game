import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Game, Player


# 🏠 HOME PAGE
def home(request):
    return render(request, 'home.html')


# 🎮 GAME VIEW
def game_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    current_player = game.player1 if game.turn % 2 == 1 else game.player2
    context = {
        'game': game,
        'player1': game.player1,
        'player2': game.player2,
        'current_player': current_player,
    }
    return render(request, 'game.html', context)


# ⚔️ ATTACK — Balanced standard strike
def attack(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    attacker = game.player1 if game.turn % 2 == 1 else game.player2
    defender = game.player2 if game.turn % 2 == 1 else game.player1

    base_damage = attacker.attack - defender.defense
    random_bonus = random.randint(0, 5)
    damage = max(base_damage + random_bonus, 1)

    # 🌟 CRITICAL HIT (10% chance)
    critical = random.random() < 0.10
    if critical:
        damage *= 2

    # 🛡️ BLOCK REDUCTION
    if defender.defending:
        damage = damage // 2
        defender.defending = False

    defender.health -= damage
    if defender.health <= 0:
        defender.health = 0
        game.is_over = True
        game.winner = attacker.user.username

    defender.save()
    game.last_damage = damage
    if critical:
        game.last_action = f"💥 CRITICAL! {attacker.user.username} obliterated {defender.user.username} for {damage} damage!"
    else:
        game.last_action = f"{attacker.user.username} struck {defender.user.username} for {damage} damage ⚔️"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# 💥 HEAVY ATTACK — Slow but devastating (25% miss chance)
def heavy(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    attacker = game.player1 if game.turn % 2 == 1 else game.player2
    defender = game.player2 if game.turn % 2 == 1 else game.player1

    # 🎲 25% CHANCE TO MISS
    if random.random() < 0.25:
        game.last_action = f"{attacker.user.username}'s heavy swing missed! 💨"
        game.last_damage = 0
        game.turn += 1
        game.save()
        return redirect('game', game_id=game.id)

    base_damage = attacker.attack * 2 - defender.defense
    random_bonus = random.randint(2, 8)
    damage = max(base_damage + random_bonus, 5)

    # 🌟 CRITICAL (8% chance — lower than normal attack)
    critical = random.random() < 0.08
    if critical:
        damage = int(damage * 1.8)

    if defender.defending:
        damage = damage // 2
        defender.defending = False

    defender.health -= damage
    if defender.health <= 0:
        defender.health = 0
        game.is_over = True
        game.winner = attacker.user.username

    defender.save()
    game.last_damage = damage
    if critical:
        game.last_action = f"💥 CRITICAL HEAVY! {attacker.user.username} crushed {defender.user.username} for {damage} damage!"
    else:
        game.last_action = f"💪 {attacker.user.username} landed a HEAVY HIT on {defender.user.username} for {damage} damage!"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# ⚡ QUICK ATTACK — Fast but weak (never misses)
def quick(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    attacker = game.player1 if game.turn % 2 == 1 else game.player2
    defender = game.player2 if game.turn % 2 == 1 else game.player1

    # Quick attacks never miss and ignore some defense
    base_damage = max(attacker.attack - defender.defense // 2, 1)
    random_bonus = random.randint(0, 3)
    damage = base_damage + random_bonus

    # 🌟 CRITICAL (12% chance — slightly higher due to speed)
    critical = random.random() < 0.12
    if critical:
        damage *= 2

    if defender.defending:
        damage = max(damage // 2, 1)
        defender.defending = False

    defender.health -= damage
    if defender.health <= 0:
        defender.health = 0
        game.is_over = True
        game.winner = attacker.user.username

    defender.save()
    game.last_damage = damage
    if critical:
        game.last_action = f"⚡ CRITICAL QUICK! {attacker.user.username} struck {defender.user.username} for {damage} damage!"
    else:
        game.last_action = f"⚡ {attacker.user.username} landed a quick strike on {defender.user.username} for {damage} damage!"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# 🛡️ DEFEND — Halves next incoming damage
def defend(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    player = game.player1 if game.turn % 2 == 1 else game.player2
    player.defending = True
    player.save()

    game.last_damage = 0
    game.last_action = f"{player.user.username} raises their shield 🛡️"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# 🔄 COUNTER — Punish defending opponents (50% fail risk)
def counter(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    attacker = game.player1 if game.turn % 2 == 1 else game.player2
    defender = game.player2 if game.turn % 2 == 1 else game.player1

    # ❌ FAIL if opponent is NOT defending (50% chance)
    if not defender.defending:
        if random.random() < 0.50:
            game.last_action = f"{attacker.user.username} tried to counter but {defender.user.username} wasn't defending! ❌"
            game.last_damage = 0
            game.turn += 1
            game.save()
            return redirect('game', game_id=game.id)

    # ✅ SUCCESS — Breaks through defense for big damage
    defender.defending = False
    base_damage = int(attacker.attack * 1.5)
    random_bonus = random.randint(3, 8)
    damage = max(base_damage + random_bonus, 8)

    # 🌟 CRITICAL (15% chance — higher reward for smart play)
    critical = random.random() < 0.15
    if critical:
        damage = int(damage * 1.7)

    defender.health -= damage
    if defender.health <= 0:
        defender.health = 0
        game.is_over = True
        game.winner = attacker.user.username

    defender.save()
    game.last_damage = damage
    if critical:
        game.last_action = f"🔄 CRITICAL COUNTER! {attacker.user.username} broke through {defender.user.username}'s guard for {damage} damage!"
    else:
        game.last_action = f"🔄 {attacker.user.username} countered {defender.user.username}'s defense for {damage} damage!"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# ⚡ DODGE — Avoid the next attack (50% chance to fail)
def dodge(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    player = game.player1 if game.turn % 2 == 1 else game.player2

    # 🎲 50% CHANCE TO FAIL DODGE
    if random.random() < 0.50:
        game.last_action = f"{player.user.username} tried to dodge but tripped! ❌"
        game.last_damage = 0
        game.turn += 1
        game.save()
        return redirect('game', game_id=game.id)

    # ✅ SUCCESS — sets dodge flag (consumed by next incoming attack)
    player.defending = False  # Clear any existing defend
    player.save()

    game.last_damage = 0
    game.last_action = f"{player.user.username} dodged out of the way! ⚡"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# 🌟 SPECIAL MOVE — Character signature attack (costs 20 HP)
def special(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)
    if game.is_over:
        return redirect('game', game_id=game.id)

    attacker = game.player1 if game.turn % 2 == 1 else game.player2
    defender = game.player2 if game.turn % 2 == 1 else game.player1

    if attacker.health <= 20:
        game.last_action = f"{attacker.user.username} is too weak to use a special move!"
        game.save()
        return redirect('game', game_id=game.id)

    attacker.health -= 20
    damage = random.randint(25, 40)

    # 🌟 CRITICAL (15% chance)
    critical = random.random() < 0.15
    if critical:
        damage = int(damage * 1.6)

    if defender.defending:
        damage = damage // 2
        defender.defending = False

    defender.health -= damage
    if defender.health <= 0:
        defender.health = 0
        game.is_over = True
        game.winner = attacker.user.username

    attacker.save()
    defender.save()
    game.last_damage = damage
    if critical:
        game.last_action = f"🌟 CRITICAL SPECIAL! {attacker.user.username} unleashed devastation on {defender.user.username} for {damage} damage! (cost 20 HP)"
    else:
        game.last_action = f"🌟 {attacker.user.username} unleashed a SPECIAL MOVE on {defender.user.username} for {damage} damage! (cost 20 HP)"
    game.turn += 1
    game.save()
    return redirect('game', game_id=game.id)


# 🔄 RESTART GAME
def restart(request, game_id):
    if request.method != 'POST':
        return redirect('game', game_id=game_id)
    game = get_object_or_404(Game, id=game_id)

    for player in [game.player1, game.player2]:
        player.health = 100
        player.defending = False
        player.save()

    game.turn = 1
    game.is_over = False
    game.last_damage = 0
    game.last_action = "A new battle begins..."
    game.winner = ""
    game.save()
    return redirect('game', game_id=game.id)