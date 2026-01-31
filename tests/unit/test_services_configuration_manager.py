# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.configuration_manager module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from asyncplatform import context
from asyncplatform.services.configuration_manager import Service


class TestConfigurationManagerServiceInitialization:
    """Test suite for Configuration Manager Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute."""
        assert hasattr(Service, "name")
        assert Service.name == "configuration_manager"

    def test_service_init_with_context(self):
        """Test Service initialization with context."""
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestConfigurationManagerGetDevices:
    """Test suite for get_devices method."""

    @pytest.mark.asyncio
    async def test_get_devices_returns_device_list(self):
        """Test get_devices returns list of devices."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity": "device",
            "total": 2,
            "unique_device_count": 2,
            "return_count": 2,
            "start_index": 0,
            "list": [
                {"name": "device1", "address": "10.0.0.1"},
                {"name": "device2", "address": "10.0.0.2"},
            ],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_devices()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "device1"
        assert result[1]["name"] == "device2"

    @pytest.mark.asyncio
    async def test_get_devices_with_filter(self):
        """Test get_devices with filter parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity": "device",
            "total": 1,
            "unique_device_count": 1,
            "return_count": 1,
            "start_index": 0,
            "list": [{"name": "device1", "address": "10.0.0.1"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_devices(filter={"name": "device1"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "device1"

        # Verify correct parameters were passed
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["filter"] == {"name": "device1"}

    @pytest.mark.asyncio
    async def test_get_devices_with_automatic_pagination(self):
        """Test get_devices handles automatic pagination."""
        ctx = context.Context()
        mock_client = Mock()

        # First page
        page1 = Mock()
        page1.json.return_value = {
            "entity": "device",
            "total": 250,
            "list": [{"name": f"device{i}"} for i in range(100)],
        }

        # Subsequent pages
        page2 = Mock()
        page2.json.return_value = {
            "entity": "device",
            "total": 250,
            "list": [{"name": f"device{i}"} for i in range(100, 200)],
        }

        page3 = Mock()
        page3.json.return_value = {
            "entity": "device",
            "total": 250,
            "list": [{"name": f"device{i}"} for i in range(200, 250)],
        }

        mock_client.post = AsyncMock(side_effect=[page1, page2, page3])
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_devices()

        # Verify all pages were fetched
        assert len(result) == 250
        assert result[0]["name"] == "device0"
        assert result[249]["name"] == "device249"

    @pytest.mark.asyncio
    async def test_get_devices_with_empty_results(self):
        """Test get_devices handles empty results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity": "device",
            "total": 0,
            "list": [],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_devices()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_devices_with_adapter_filters(self):
        """Test get_devices with adapter type and ID filters."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity": "device",
            "total": 1,
            "list": [{"name": "device1", "adapter": "NSO"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_devices(
            adapter_type=["NSO"], adapter_id=["nso-us"], exact_match=True
        )

        assert len(result) == 1
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["adapterType"] == ["NSO"]
        assert payload["options"]["adapterId"] == ["nso-us"]
        assert payload["options"]["exactMatch"] is True

    @pytest.mark.asyncio
    async def test_get_devices_pagination_with_exception(self):
        """Test get_devices handles exceptions during pagination."""
        ctx = context.Context()
        mock_client = Mock()

        page1 = Mock()
        page1.json.return_value = {
            "entity": "device",
            "total": 250,
            "list": [{"name": f"device{i}"} for i in range(100)],
        }

        # Second page raises exception
        mock_client.post = AsyncMock(side_effect=[page1, Exception("Network error")])
        ctx.client = mock_client

        service = Service(ctx)

        with pytest.raises(Exception, match="Network error"):
            await service.get_devices()


class TestConfigurationManagerGetDevice:
    """Test suite for get_device method."""

    @pytest.mark.asyncio
    async def test_get_device_returns_device_data(self):
        """Test get_device returns device details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "device1",
            "address": "10.0.0.1",
            "port": "22",
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_device("device1")

        assert result["name"] == "device1"
        assert result["address"] == "10.0.0.1"

        # Verify correct endpoint was called
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/devices/device1"

    @pytest.mark.asyncio
    async def test_check_device_alive(self):
        """Test check_device_alive returns device status."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"alive": True, "reachable": True}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.check_device_alive("device1")

        assert result["alive"] is True
        assert result["reachable"] is True

        # Verify correct endpoint was called
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/devices/device1/isAlive"


class TestConfigurationManagerBackups:
    """Test suite for backup management methods."""

    @pytest.mark.asyncio
    async def test_get_backups_returns_backup_list(self):
        """Test get_backups returns list of backups."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 2,
            "list": [
                {"_id": "backup1", "name": "device1", "date": "2025-01-01"},
                {"_id": "backup2", "name": "device2", "date": "2025-01-02"},
            ],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_backups()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["_id"] == "backup1"

    @pytest.mark.asyncio
    async def test_get_backup_returns_single_backup(self):
        """Test get_backup returns specific backup details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "backup1",
            "name": "device1",
            "date": "2025-01-01",
            "config": "...",
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_backup("backup1")

        assert result["_id"] == "backup1"
        assert result["name"] == "device1"

    @pytest.mark.asyncio
    async def test_delete_backups_removes_backups(self):
        """Test delete_backups removes specified backups."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "deleted": 2}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.delete_backups(["backup1", "backup2"])

        assert result["status"] == "success"
        assert result["deleted"] == 2

    @pytest.mark.asyncio
    async def test_get_backups_with_empty_results(self):
        """Test get_backups handles empty results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 0,
            "list": [],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_backups()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_backups_with_automatic_pagination(self):
        """Test get_backups handles automatic pagination."""
        ctx = context.Context()
        mock_client = Mock()

        page1 = Mock()
        page1.json.return_value = {
            "total": 150,
            "list": [{"_id": f"backup{i}"} for i in range(100)],
        }

        page2 = Mock()
        page2.json.return_value = {
            "total": 150,
            "list": [{"_id": f"backup{i}"} for i in range(100, 150)],
        }

        mock_client.post = AsyncMock(side_effect=[page1, page2])
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_backups(filter={"name": "router"}, regex=True)

        assert len(result) == 150
        call_args = mock_client.post.call_args_list[0]
        payload = call_args[1]["json"]
        assert payload["options"]["filter"] == {"name": "router"}
        assert payload["options"]["regex"] is True

    @pytest.mark.asyncio
    async def test_get_backups_pagination_with_exception(self):
        """Test get_backups handles exceptions during pagination."""
        ctx = context.Context()
        mock_client = Mock()

        page1 = Mock()
        page1.json.return_value = {
            "total": 150,
            "list": [{"_id": f"backup{i}"} for i in range(100)],
        }

        mock_client.post = AsyncMock(side_effect=[page1, Exception("API error")])
        ctx.client = mock_client

        service = Service(ctx)

        with pytest.raises(Exception, match="API error"):
            await service.get_backups()


class TestConfigurationManagerDeviceGroups:
    """Test suite for device group management methods."""

    @pytest.mark.asyncio
    async def test_get_device_groups_returns_group_list(self):
        """Test get_device_groups returns list of device groups."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"_id": "group1", "name": "Group1"},
            {"_id": "group2", "name": "Group2"},
        ]
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_device_groups()

        assert len(result) == 2
        assert result[0]["name"] == "Group1"

    @pytest.mark.asyncio
    async def test_get_device_group_returns_single_group(self):
        """Test get_device_group returns specific group details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "group1",
            "name": "Group1",
            "devices": ["device1", "device2"],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_device_group("group1")

        assert result["_id"] == "group1"
        assert result["name"] == "Group1"
        assert len(result["devices"]) == 2

    @pytest.mark.asyncio
    async def test_delete_device_groups_removes_groups(self):
        """Test delete_device_groups removes specified groups."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "deleted": 1}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.delete_device_groups(["group1"])

        assert result["status"] == "success"
        assert result["deleted"] == 1

    @pytest.mark.asyncio
    async def test_search_device_groups(self):
        """Test search_device_groups returns search results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [{"_id": "group1", "name": "SearchGroup"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        query = {"name": "SearchGroup"}
        result = await service.search_device_groups(query)

        assert result["total"] == 1
        assert result["results"][0]["name"] == "SearchGroup"

        # Verify correct endpoint and payload
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/configuration_manager/deviceGroups/search"
        assert call_args[1]["json"] == query


class TestConfigurationManagerCompliancePlans:
    """Test suite for compliance plan management methods."""

    @pytest.mark.asyncio
    async def test_create_compliance_plan_returns_plan_data(self):
        """Test create_compliance_plan returns created plan details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "plan1",
            "name": "TestPlan",
            "description": "Test compliance plan",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.create_compliance_plan(
            "TestPlan", description="Test compliance plan"
        )

        assert result["_id"] == "plan1"
        assert result["name"] == "TestPlan"

    @pytest.mark.asyncio
    async def test_update_compliance_plan_updates_plan(self):
        """Test update_compliance_plan updates plan details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "message": "Compliance Plan updated",
        }
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.update_compliance_plan(
            "plan1", name="UpdatedPlan", description="Updated description"
        )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_compliance_plans_removes_plans(self):
        """Test delete_compliance_plans removes specified plans."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "deleted": 2}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.delete_compliance_plans(["plan1", "plan2"])

        assert result["status"] == "success"
        assert result["deleted"] == 2

    @pytest.mark.asyncio
    async def test_create_compliance_plan_with_nodes(self):
        """Test create_compliance_plan with nodes parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "plan1",
            "name": "TestPlan",
            "nodes": [{"treeId": "tree1", "version": "1.0"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        nodes = [{"treeId": "tree1", "version": "1.0", "nodeId": "node1"}]
        result = await service.create_compliance_plan("TestPlan", nodes=nodes)

        assert result["_id"] == "plan1"
        assert len(result["nodes"]) == 1

    @pytest.mark.asyncio
    async def test_update_compliance_plan_with_all_params(self):
        """Test update_compliance_plan with all parameters."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "message": "Compliance Plan updated",
        }
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.update_compliance_plan(
            "plan1",
            name="UpdatedPlan",
            description="Updated",
            nodes=[{"treeId": "tree1"}],
            gbac={"read": ["group1"], "write": ["group2"]},
        )

        assert result["status"] == "success"

        # Verify all options passed
        call_args = mock_client.put.call_args
        options = call_args[1]["json"]["options"]
        assert options["name"] == "UpdatedPlan"
        assert options["description"] == "Updated"
        assert "nodes" in options
        assert "gbac" in options

    @pytest.mark.asyncio
    async def test_get_compliance_plan(self):
        """Test get_compliance_plan returns plan details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "_id": "plan1",
            "name": "TestPlan",
            "description": "Test",
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_compliance_plan("plan1")

        assert result["_id"] == "plan1"
        assert result["name"] == "TestPlan"

        # Verify correct endpoint
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/compliance_plans/plan1"

    @pytest.mark.asyncio
    async def test_search_compliance_plans(self):
        """Test search_compliance_plans returns search results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [{"_id": "plan1", "name": "TestPlan"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        query = {"name": "TestPlan"}
        result = await service.search_compliance_plans(query)

        assert result["total"] == 1
        assert result["results"][0]["name"] == "TestPlan"

    @pytest.mark.asyncio
    async def test_run_compliance_plan(self):
        """Test run_compliance_plan executes plan."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "jobId": "job123",
            "status": "running",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        plan_data = {"planId": "plan1", "devices": ["device1"]}
        result = await service.run_compliance_plan(plan_data)

        assert result["jobId"] == "job123"
        assert result["status"] == "running"

        # Verify correct endpoint
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/configuration_manager/compliance_plans/run"


class TestConfigurationManagerTemplates:
    """Test suite for template management methods."""

    @pytest.mark.asyncio
    async def test_create_template_returns_template_data(self):
        """Test create_template returns created template details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": "success",
            "data": {
                "id": "template1",
                "name": "TestTemplate",
                "template": "interface {{ name }}",
            },
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.create_template(
            "TestTemplate", "interface {{ name }}", variables={"name": "eth0"}
        )

        assert result["id"] == "template1"
        assert result["name"] == "TestTemplate"
        assert result["template"] == "interface {{ name }}"

    @pytest.mark.asyncio
    async def test_update_template_updates_template(self):
        """Test update_template updates template details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "updated": 1}
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.update_template(
            "template1", name="UpdatedTemplate", template="interface {{ new_name }}"
        )

        assert result["status"] == "success"
        assert result["updated"] == 1

    @pytest.mark.asyncio
    async def test_delete_templates_removes_templates(self):
        """Test delete_templates removes specified templates."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "deleted": 2}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.delete_templates(["template1", "template2"])

        assert result["status"] == "success"
        assert result["deleted"] == 2

    @pytest.mark.asyncio
    async def test_get_templates_returns_template_list(self):
        """Test get_templates returns list of templates."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 2,
            "list": [
                {"id": "template1", "name": "Template1"},
                {"id": "template2", "name": "Template2"},
            ],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_templates()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Template1"
        assert result[1]["name"] == "Template2"

    @pytest.mark.asyncio
    async def test_get_templates_with_name_and_options(self):
        """Test get_templates with name and options parameters."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 1,
            "list": [{"id": "template1", "name": "SpecificTemplate"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_templates(
            name="SpecificTemplate", options={"limit": 10}
        )

        assert len(result) == 1
        assert result[0]["name"] == "SpecificTemplate"

        # Verify parameters passed
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["name"] == "SpecificTemplate"
        assert payload["options"] == {"limit": 10}

    @pytest.mark.asyncio
    async def test_create_template_with_device_os_types(self):
        """Test create_template with device_os_types parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": "success",
            "data": {
                "id": "template1",
                "name": "TestTemplate",
                "template": "config",
                "deviceOSTypes": ["ios", "nxos"],
            },
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.create_template(
            "TestTemplate",
            "config",
            variables={"var1": "val1"},
            device_os_types=["ios", "nxos"],
        )

        assert result["id"] == "template1"
        assert "deviceOSTypes" in result

        # Verify device_os_types passed
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["deviceOSTypes"] == ["ios", "nxos"]

    @pytest.mark.asyncio
    async def test_update_template_with_device_os_types(self):
        """Test update_template with device_os_types parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "updated": 1}
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.update_template(
            "template1",
            name="Updated",
            template="new config",
            variables={"var2": "val2"},
            device_os_types=["ios-xe"],
        )

        assert result["status"] == "success"

        # Verify all parameters passed
        call_args = mock_client.put.call_args
        payload = call_args[1]["json"]
        assert payload["data"]["name"] == "Updated"
        assert payload["data"]["template"] == "new config"
        assert payload["data"]["variables"] == {"var2": "val2"}
        assert payload["options"]["deviceOSTypes"] == ["ios-xe"]

    @pytest.mark.asyncio
    async def test_apply_template(self):
        """Test apply_template applies template to devices."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "jobId": "job456",
            "status": "submitted",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        template_data = {
            "templateId": "template1",
            "devices": ["device1", "device2"],
            "variables": {"var1": "value1"},
        }
        result = await service.apply_template(template_data)

        assert result["jobId"] == "job456"
        assert result["status"] == "submitted"

        # Verify correct endpoint
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/configuration_manager/templates/apply"
        assert call_args[1]["json"] == template_data


class TestConfigurationManagerDeviceConfiguration:
    """Test suite for device configuration methods."""

    @pytest.mark.asyncio
    async def test_get_device_configuration_without_format(self):
        """Test get_device_configuration without format parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"config": "interface eth0..."}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_device_configuration("device1")

        assert "config" in result

        # Verify correct endpoint was called
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/devices/device1/configuration"

    @pytest.mark.asyncio
    async def test_get_device_configuration_with_format(self):
        """Test get_device_configuration with format parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"config": "<xml>...</xml>"}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        await service.get_device_configuration("device1", format="xml")

        # Verify correct endpoint was called with format
        call_args = mock_client.get.call_args
        assert (
            call_args[0][0]
            == "/configuration_manager/devices/device1/configuration/xml"
        )

    @pytest.mark.asyncio
    async def test_patch_device_updates_device(self):
        """Test patch_device updates device configuration."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.patch_device("device1", {"name": "new_name"})

        assert result["status"] == "success"

        # Verify correct endpoint was called
        call_args = mock_client.patch.call_args
        assert call_args[0][0] == "/configuration_manager/patch_device/device1"

    @pytest.mark.asyncio
    async def test_patch_device_with_advanced_mode(self):
        """Test patch_device with advanced mode enabled."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        await service.patch_device("device1", {"name": "new_name"}, advanced=True)

        # Verify advanced endpoint was called
        call_args = mock_client.patch.call_args
        assert call_args[0][0] == "/configuration_manager/patch_device/advanced/device1"


class TestConfigurationManagerComplianceReports:
    """Test suite for compliance report methods."""

    @pytest.mark.asyncio
    async def test_get_compliance_reports_without_query(self):
        """Test get_compliance_reports without query parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "reports": [{"id": "report1"}, {"id": "report2"}]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_compliance_reports()

        assert "reports" in result

    @pytest.mark.asyncio
    async def test_get_compliance_report_details(self):
        """Test get_compliance_report_details returns report details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "report1",
            "status": "completed",
            "details": {},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_compliance_report_details("report1")

        assert result["id"] == "report1"
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_compliance_reports_with_query(self):
        """Test get_compliance_reports with query parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 1,
            "reports": [{"id": "report1", "device": "device1"}],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        query = {"device": "device1"}
        result = await service.get_compliance_reports(query=query)

        assert result["total"] == 1
        assert result["reports"][0]["device"] == "device1"

        # Verify POST was used with query
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/configuration_manager/compliance_reports"
        assert call_args[1]["json"] == query

    @pytest.mark.asyncio
    async def test_get_compliance_report_history_without_query(self):
        """Test get_compliance_report_history without query parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "history": [{"reportId": "report1", "date": "2025-01-01"}]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_compliance_report_history()

        assert "history" in result
        assert len(result["history"]) == 1

        # Verify GET was used
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/compliance_reports/history"

    @pytest.mark.asyncio
    async def test_get_compliance_report_history_with_query(self):
        """Test get_compliance_report_history with query parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "history": [{"reportId": "report1", "device": "device1"}]
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        query = {"device": "device1", "startDate": "2025-01-01"}
        result = await service.get_compliance_report_history(query=query)

        assert "history" in result
        assert result["history"][0]["device"] == "device1"

        # Verify POST was used with query
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/configuration_manager/compliance_reports/history"
        assert call_args[1]["json"] == query


class TestConfigurationManagerConfigurations:
    """Test suite for configuration management methods."""

    @pytest.mark.asyncio
    async def test_get_configs_with_tree_id_only(self):
        """Test get_configs with only tree_id parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "treeId": "tree1",
            "versions": ["1.0", "1.1"],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_configs("tree1")

        assert result["treeId"] == "tree1"
        assert len(result["versions"]) == 2

        # Verify correct endpoint
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/configs/tree1"

    @pytest.mark.asyncio
    async def test_get_configs_with_version(self):
        """Test get_configs with tree_id and version parameters."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "treeId": "tree1",
            "version": "1.0",
            "nodes": ["node1", "node2"],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_configs("tree1", version="1.0")

        assert result["treeId"] == "tree1"
        assert result["version"] == "1.0"

        # Verify correct endpoint
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/configs/tree1/1.0"

    @pytest.mark.asyncio
    async def test_get_configs_with_version_and_node_path(self):
        """Test get_configs with all parameters."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "treeId": "tree1",
            "version": "1.0",
            "nodePath": "root/config",
            "data": {"key": "value"},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_configs(
            "tree1", version="1.0", node_path="root/config"
        )

        assert result["treeId"] == "tree1"
        assert result["nodePath"] == "root/config"

        # Verify correct endpoint
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/configuration_manager/configs/tree1/1.0/root/config"

    @pytest.mark.asyncio
    async def test_search_configs(self):
        """Test search_configs returns search results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 2,
            "results": [
                {"treeId": "tree1", "version": "1.0"},
                {"treeId": "tree2", "version": "2.0"},
            ],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        query = {"type": "golden-config"}
        result = await service.search_configs(query)

        assert result["total"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["treeId"] == "tree1"

        # Verify correct endpoint and payload
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/configuration_manager/search/configs"
        assert call_args[1]["json"] == query
