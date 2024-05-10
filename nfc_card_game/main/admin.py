from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.game_settings import GameSettings
from nfc_card_game.main.models.trading import (
    Post,
    Mine,
    PlayerItem,
    PostRecipe,
    TeamMine,
    Item,
    TeamMineItem,
)

from nfc_card_game.main.models.player import Team, Player


@admin.register(GameSettings)
class GameModeAdmin(admin.ModelAdmin):
    list_display = ["mode"]


@admin.register(Activity)
class Activities(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "link"]

    @mark_safe
    def link(self, obj):
        card_url = reverse("post", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')


class PlayerInLine(admin.TabularInline):
    model = Player


class MineInLine(admin.TabularInline):
    model = Mine


class PlayerItemInline(admin.TabularInline):
    model = PlayerItem


class PostRecipeInline(admin.TabularInline):
    model = PostRecipe


class TeamMineItemInline(admin.TabularInline):
    model = TeamMineItem

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs["queryset"] = Item.objects.filter(type="MINER")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [PlayerInLine]


class TeamMineAdmin(admin.ModelAdmin):
    list_display = ["mine", "team", "money"]
    inlines = [TeamMineItemInline]


class TeamMineItemAdmin(admin.ModelAdmin):
    list_display = ["team_mine", "item", "amount"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs["queryset"] = Item.objects.filter(type="MINER")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "team", "section", "link"]
    inlines = [PlayerItemInline]

    @mark_safe
    def link(self, obj):
        card_url = reverse("player", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')


class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "currency", "type"]
    exclude = ("type",)


class PlayerItemAdmin(admin.ModelAdmin):
    list_display = ["item", "player", "amount", "item"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "sells", "sell_amount", "link"]
    inlines = [PostRecipeInline]

    @mark_safe
    def link(self, obj):
        card_url = reverse("post", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')


class MineAdmin(admin.ModelAdmin):
    list_display = ["name", "currency", "link"]

    @mark_safe
    def link(self, obj):
        card_url = reverse("mine", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')


class PostRecipeAdmin(admin.ModelAdmin):
    list_display = ["item", "price", "post"]


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Mine, MineAdmin)
admin.site.register(TeamMine, TeamMineAdmin)
admin.site.register(TeamMineItem, TeamMineItemAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(PlayerItem, PlayerItemAdmin)
admin.site.register(PostRecipe, PostRecipeAdmin)
