"""MessageService tests"""
from typing import Final

from pytest import raises

from hellopymsdl.service.MessageService import MessageService


class TestMessageService:
    """MessageService Tests"""
    _MESSAGE_SERVICE: Final[MessageService] = MessageService("hellopymsdl_test_rsrc")

    class TestGetMessage:
        """get_message method tests"""

        class TestNominalCase:

            def test_resource_exists__should__return_message(self) -> None:
                """When resource exists, should return the resource message"""
                # GIVEN / WHEN
                message: str = TestMessageService._MESSAGE_SERVICE.get_message("test_message.txt")

                # THEN
                assert "A test message" == message

            def test_default_package_package__should__exists(self):
                """When use default package value, it should exist (ei: not raise a ModuleNotFoundError)"""
                # GIVEN
                message_service: MessageService = MessageService()

                # WHEN / THEN (FileNotFoundError means the resource package exists but not the message file)
                with raises(FileNotFoundError):
                    message_service.get_message("unknown_message.txt")

        class TestErrorCase:
            def test_resource_package_not_exists__should__raise_modulenotfoundesrror(self) -> None:
                """When resource package doesn't exist, should raise a ModuleNotFoundError"""
                # GIVEN
                message_service: MessageService = MessageService("unknown_test_rsrc")

                # WHEN / THEN
                with raises(ModuleNotFoundError):
                    message_service.get_message("test_message.txt")

            def test_none_resource_package__should__raise_attributeerror(self) -> None:
                """When resource package is None, should raise an AttributeError"""
                # GIVEN
                # noinspection PyTypeChecker
                message_service: MessageService = MessageService(None)

                # WHEN / THEN
                with raises(AttributeError):
                    message_service.get_message("test_message.txt")

            def test_resource_not_exists__should__raise_filenotfounderror(self) -> None:
                """When resource is doesn't exist, should raise a FileNotFoundError"""
                # GIVEN / WHEN / THEN
                with raises(FileNotFoundError):
                    TestMessageService._MESSAGE_SERVICE.get_message("unknown_message.txt")

            def test_none_resource__should__raise_typeerror(self) -> None:
                """When resource is None, should raise an TypeError"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    TestMessageService._MESSAGE_SERVICE.get_message(None)
