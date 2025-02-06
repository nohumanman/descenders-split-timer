using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using ModLoaderSolution;
using System;

namespace ModLoaderSolution
{
	public class BikeSwitcher : MonoBehaviour
	{
        public string oldBike;
        public void Start(){
            oldBike = GetBike();
        }
        public void ToBike(string bike, string id)
        {
            using (new MethodAnalysis())
            {
                Utilities.Log("id " + id + " switching to bike '" + bike + "'");
                if (Utilities.instance.isInReplayMode())
                    return;
                GameObject playerObject = Utilities.GetPlayerFromId(id);
                if (playerObject == null)
                    return;
                // if it's us, let the server know
                if (playerObject == Utilities.GetPlayer())                    
                    PlayerManagement.Instance.OnBikeSwitch(bike);
                // get bike type id
                int bikeType = Utilities.instance.GetBikeInt(bike);
                // if it's us, update our preferred bike
                if (id == (new PlayerIdentification.SteamIntegration()).getSteamId())
                    FindObjectOfType<PrefsManager>().SetInt("PREFERREDBIKE", bikeType);
                // finally, set the bike
                Utilities.instance.SetBike(Utilities.GetPlayerInfoImpactFromId(id), bikeType);
            }
        }
        static PrefsManager prefsManager;
        public static string GetBike(){
            using (new MethodAnalysis())
            {
                // if prefsManager does not exist, find it
                if (prefsManager == null)
                    prefsManager = FindObjectOfType<PrefsManager>();
                // get preferred bike from prefsManager
                int pref = prefsManager.GetInt("PREFERREDBIKE");
                // convert to text
                switch (pref)
                {
                    case 0:
                        return "enduro";
                    case 1:
                        return "downhill";
                    case 2:
                        return "hardtail";
                }
                throw new Exception("Bike cannot be found!");
            }
        }
    }
}