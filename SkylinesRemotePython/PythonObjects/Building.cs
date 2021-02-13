﻿using SkylinesPythonShared;
using SkylinesPythonShared.API;
using System;
using System.Collections.Generic;
using System.Text;

namespace SkylinesRemotePython.API
{
    public class Building : ObjectAPI
    {
        public int id { get; private set; }

        public string prefab_name { get; private set; }

        public Vector position { get; private set; }

        public double angle { get; private set; }

        public void refresh()
        {
            AssignData(api.client.RemoteCall<BuildingMessage>(Contracts.GetBuildingFromId, id));
        }

        internal void AssignData(BuildingMessage msg)
        {
            id = msg.id;
            prefab_name = msg.prefab_name;
            position = msg.position;
            angle = msg.angle;
        }
        internal Building(BuildingMessage obj, GameAPI api) : base(api)
        {
            AssignData(obj);
        }
    }
}