from django.contrib import admin

from nfc_card_game.main.models import Player, Team

# Register your models here.


class PlayerInLine(admin.TabularInline):
    model = Player


class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [PlayerInLine]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "team", "section"]


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
