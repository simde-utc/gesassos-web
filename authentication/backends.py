#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from cas.backends import CASBackend
from cas.backends import _verify
from django.contrib.auth import get_user_model
from django.conf import settings
import datetime
from authentication.models import UserType, UserRole
from django.contrib.auth.models import Group
from api import portal, gingerV1


class UpdatedCASBackend(CASBackend):
    """
    An extension of the CASBackend to make it functionnable 
    with custom user models on user creation and selection
    """

    def authenticate(self, ticket, service):
        """
        Verifies CAS ticket and gets or creates User object
        NB: Use of PT to identify proxy
        """

        UserModel = get_user_model()
        username = _verify(ticket, service)
        if not username:
            return None

        try:
            user = UserModel._default_manager.get(**{
                UserModel.USERNAME_FIELD: username
            })
            user = self.configure_user(user)
            user.save()
        except UserModel.DoesNotExist:
            # user will have an "unusable" password
            if settings.CAS_AUTO_CREATE_USER:
                user = UserModel.objects.create_user(username, '')
                user = self.configure_user(user)
                user.save()
            else:
                user = None
        return user

    def configure_user(self, user):
        """
        Configures a user in a custom manner
        :param user: the user to retrieve informations on
        :return: a configured user
        """
        return user


class GingerCASBackend(UpdatedCASBackend):
    """
    A CAS Backend implementing Ginger for User configuration
    """

    def configure_user(self, user):
        """
        Configures a user using Ginger and the student organization portal
        :param user: The User to configure
        :return: The configurated user
        """

        # GINGER
        ginger_user = gingerV1.get_user(user)

        user.first_name = ginger_user['surname'].capitalize()
        user.last_name = ginger_user['name'].capitalize()
        user.email = ginger_user['email']
        if ginger_user['is_adult']:
            user.birthdate = datetime.date.min
        else:
            user.birthdate = datetime.date.today
        # print(json_data)

        try:
            UserType.objects.get(
                name=UserType.NON_COTISANT)
        except Exception as e:
            UserType.init_values()
            raise e

        if ginger_user['is_contributor']:
            user.usertype = UserType.objects.get(
                name=UserType.COTISANT)
        else:
            user.usertype = UserType.objects.get(
                name=UserType.NON_COTISANT)

        # PORTAL RIGHTS
        superadmin, groups, roles = portal.get_roles(user)

        self._test_groups()
        self._reset_user_rights(user)

        # Check and save SiMDE and BDE rights (portal groups and super admin)
        if groups:
            for group in groups:
                if group == "simde":
                    self._set_user_simde(user)
                if group == "bde":
                    self._set_user_bde(user)
        if superadmin:
            self._set_user_superadmin(user)

        # TODO remove, test only
        if user.get_username() in ["michelme", "jennypau", "snastuzz", "crichard"]:
            # self._set_user_superadmin(user)
            self._set_user_simde(user)
            # self._set_user_bde(user)
            self._set_user_geek(user, "festupic")
            self._set_user_geek(user, "simde")
            self._set_user_president(user, "etuville")

        # Check and save asso rights
        if roles:
            for role in roles:
                # For all role that is president, "board", "resp info", save them
                if role["role"]["name"] == u"Président":
                    self._set_user_president(user, role["asso"]["login"])
                if role["role"]["bureau"]:
                    self._set_user_board(user, role["asso"]["login"])
                if role["role"]["name"] == u"Resp Info":
                    self._set_user_geek(user, role["asso"]["login"])

        return user



    # rights getter/setters
    def _test_groups(self):
        Group.objects.get_or_create(name="simde")
        Group.objects.get_or_create(name="bde")
        Group.objects.get_or_create(name="president")
        Group.objects.get_or_create(name="board")
        Group.objects.get_or_create(name="geek")

    def _reset_user_rights(self, user):
        user.groups.clear()
        user.roles.all().delete() # TODO check this works
        user.is_superuser = False

    def _set_user_simde(self, user):
        print("%s is in SiMDE" % user.get_username())
        g = Group.objects.get(name="simde")
        g.user_set.add(user)

    def _set_user_bde(self, user):
        print("%s is in BDE" % user.get_username())
        g = Group.objects.get(name="bde")
        g.user_set.add(user)

    def _set_user_superadmin(self, user):
        print("%s is in superadmin" % user.get_username())
        user.is_superuser = True

    def _set_user_president(self, user, asso_name):
        print("%s is president in %s" % (user.get_username(), asso_name))
        print("ERROR: TODO set_president")
        # Add role
        user.roles.create(role=UserRole.PRESIDENT, asso=asso_name)
        # Add to president group
        g = Group.objects.get(name="president")
        g.user_set.add(user)

    def _set_user_board(self, user, asso_name):
        print("%s is board in %s" % (user.get_username(), asso_name))
        print("ERROR: TODO TEST set_board")
        # Add role
        user.roles.create(role=UserRole.BOARD, asso=asso_name)
        # Add to board group
        g = Group.objects.get(name="board")
        g.user_set.add(user)

    def _set_user_geek(self, user, asso_name):
        print("%s is geek in %s" % (user.get_username(), asso_name))
        print("ERROR: TODO TEST set_geek")
        # Add role
        user.roles.create(role=UserRole.GEEK, asso=asso_name)
        # Add to geek group
        g = Group.objects.get(name="geek")
        g.user_set.add(user)
