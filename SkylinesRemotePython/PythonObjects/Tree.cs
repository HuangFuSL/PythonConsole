﻿using SkylinesPythonShared;
using SkylinesPythonShared.API;
using System;
using System.Collections.Generic;
using System.Text;

namespace SkylinesRemotePython.API
{
    public class Tree : CitiesObject
    {
        public override string type => "tree";

        public string prefab_name { get; private set; }

        public void move(IPositionable pos) => MoveImpl(pos.position, null);

        public override void refresh()
        {
            AssignData(api.client.RemoteCall<TreeMessage>(Contracts.GetTreeFromId, id));
        }

        internal override void AssignData(InstanceMessage data)
        {
            TreeMessage msg = data as TreeMessage;
            if (msg == null) {
                deleted = true;
                return;
            }
            id = msg.id;
            prefab_name = msg.prefab_name;
            _position = msg.position;
        }
        internal Tree(TreeMessage obj, GameAPI api) : base(api)
        {
            AssignData(obj);
        }

        public override string ToString()
        {
            return "{" + "\n" +
                "type: " + type + "\n" +
                "id: " + id + "\n" +
                "position: " + pos + "\n" +
                "prefab_name: " + prefab_name + "\n" +
                "}";
        }
    }
}