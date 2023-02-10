import asyncio

from rest_framework.serializers import BaseSerializer as DRFBaseSerializer
from rest_framework.fields import empty


class BaseSerializer(DRFBaseSerializer):

    def sync_run_validation(self, data=empty):

        return super().run_validation(self, data)

    async def async_run_validation(self, data=empty):

        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = self.to_internal_value(data)

        await self.async_run_validators(value)
        return value

    def run_validation(self, data=empty):
        if getattr(self, "serializer_is_async", False):
            return self.async_run_validation(data)
        else:
            return self.sync_run_validation(data)

    async def async_run_validators(self, value):
        validator_calls = []

        for validator in self.validators:
            if getattr(validator, "requires_context", False):
                validator_calls.append(validator(value, self))
            else:
                validator_calls.append(validator(value))

        validation_result = await asyncio.gather(
            *validator_calls,
            return_exceptions=True
        )
