from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Q

from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.player import Player, Team
from nfc_card_game.main.models.game_settings import GameSettings
from nfc_card_game.main.models.trading import (
    Post,
    TeamMine,
    PlayerItem,
    Item,
    PostRecipe,
)


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


class TeamMineInLine(admin.TabularInline):
    model = TeamMine


class PlayerItemInline(admin.TabularInline):
    model = PlayerItem

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if obj is None:
            formset.form.base_fields["item"].queryset = Item.objects.filter(
                type__in=["MINER", "RESOURCE"]
            )
            formset.form.base_fields["amount"].initial = 20
        return formset


class PostRecipeInline(admin.TabularInline):
    model = PostRecipe

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is None:
            formset.form.base_fields["item"].queryset = Item.objects.filter(
                type__in=["MINER", "RESOURCE"]
            )
        return formset


class TeamMineAdmin(admin.ModelAdmin):
    list_display = ["mine", "team", "amount"]


class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [PlayerInLine]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "team", "section", "link"]
    inlines = [PlayerItemInline]

    @mark_safe
    def link(self, obj):
        card_url = reverse("player", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')


class PlayerItemAdmin(admin.ModelAdmin):
    list_display = ["item", "player", "amount"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "sells", "sell_amount", "link"]
    inlines = [PostRecipeInline]

    @mark_safe
    def link(self, obj):
        card_url = reverse("post", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "sells":
            kwargs["queryset"] = Item.objects.filter(~Q(type="MINE"))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "team"]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        print(fields)
        if obj and obj.type == "RESOURCE":
            fields = ["name", "type"]
        if obj and obj.type == "MINER":
            fields = ["name", "type", "currency"]
        return fields


class PostRecipeAdmin(admin.ModelAdmin):
    list_display = ["item", "amount", "post"]


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(TeamMine, TeamMineAdmin)
admin.site.register(PlayerItem, PlayerItemAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(PostRecipe, PostRecipeAdmin)
