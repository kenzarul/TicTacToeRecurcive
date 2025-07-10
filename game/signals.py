from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Game, GameHistory


@receiver(pre_save, sender=Game)
def record_game_result(sender, instance, **kwargs):
    # Only proceed if there's a winner and we haven't recorded this yet
    if not instance.winner or getattr(instance, '_history_recorded', False):
        return

    # Check if this is an existing game that's being updated
    if instance.pk:
        try:
            old_game = Game.objects.get(pk=instance.pk)
            if old_game.winner:  # If winner was already set, don't record again
                return
        except Game.DoesNotExist:
            pass

    # Mark that we've processed this game
    instance._history_recorded = True

    # Determine game type and players
    is_single_player = instance.player_o in ['computer', 'random', 'minimax']
    human_player = instance.player_x if not is_single_player else (
        instance.player_x if instance.player_x and instance.player_x not in ['computer', 'random', 'minimax'] else None
    )

    if not human_player:
        return  # No human player to record stats for

    try:
        user = User.objects.get(username=human_player)
        # Determine the result for the human player
        if instance.winner == 'X' and instance.player_x == human_player:
            result = 'win'
        elif instance.winner == 'O' and instance.player_o == human_player:
            result = 'win'
        elif instance.winner == ' ':
            result = 'draw'
        else:
            result = 'loss'

        # Create exactly one history record
        GameHistory.objects.create(
            user=user,
            opponent='Computer' if is_single_player else (
                instance.player_x if human_player == instance.player_o
                else instance.player_o
            ),
            mode='single' if is_single_player else 'multi',
            result=result
        )
    except User.DoesNotExist:
        pass  # Skip if user doesn't exist