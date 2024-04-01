from django.contrib import admin

from nfc_card_game.main.models import Mine, Player, Post, Team, TeamMine

# Register your models here.


class PlayerInLine(admin.TabularInline):
    model = Player


class TeamMineInLine(admin.TabularInline):
    model = TeamMine


class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [PlayerInLine]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "team", "section"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["name", "buys", "sells"]


class MineAdmin(admin.ModelAdmin):
    list_display = ["name", "currency"]
    inlines = [TeamMineInLine]


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Mine, MineAdmin)
admin.site.register(TeamMine)
