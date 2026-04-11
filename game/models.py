from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    health = models.IntegerField(default=100)
    attack = models.IntegerField(default=10)
    defense = models.IntegerField(default=5)
    defending = models.BooleanField(default=False)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    @property
    def health_percentage(self):
        return max(self.health, 0)

    @property
    def is_alive(self):
        return self.health > 0


class Game(models.Model):
    player1 = models.ForeignKey(Player, related_name='p1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='p2', on_delete=models.CASCADE)
    turn = models.IntegerField(default=1)
    is_over = models.BooleanField(default=False)
    last_damage = models.IntegerField(default=0)
    last_action = models.CharField(max_length=200, default="The battle begins...")
    winner = models.CharField(max_length=150, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.id}: {self.player1} vs {self.player2}"

    @property
    def round_number(self):
        return (self.turn + 1) // 2




