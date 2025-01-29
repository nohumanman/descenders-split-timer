using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using ModLoaderSolution;

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
                if (id == (new PlayerIdentification.SteamIntegration()).getSteamId())
                {
                    // if it's us, let the server know
                    PlayerManagement.Instance.OnBikeSwitch(bike);
                }
                GameObject PlayerObject = Utilities.GetPlayerFromId(id);
                if (PlayerObject != null)
                {
                    GameObject BikeObject = GetBikeObject(PlayerObject);

                    int bikeType = Utilities.instance.GetBikeInt(bike);
                    // if it's us, set our preferred bike
                    if (id == (new PlayerIdentification.SteamIntegration()).getSteamId())
                        FindObjectOfType<PrefsManager>().SetInt("PREFERREDBIKE", bikeType);
                    Utilities.instance.SetBike(Utilities.GetPlayerInfoImpactFromId(id), bikeType);
                }
            }
        }
        public static string GetBike(){
            using (new MethodAnalysis())
            {
                int pref = FindObjectOfType<PrefsManager>().GetInt("PREFERREDBIKE");
                if (pref == 1)
                    return "downhill";
                else if (pref == 2)
                    return "hardtail";
                return "enduro";
            }
        }
        public Animator GetPlayerAnim(GameObject PlayerObject)
        {
            using (new MethodAnalysis())
            {
                foreach (Animator a in FindObjectsOfType<Animator>())
                    if (a.name == "character_clothed_ragdoll" && a.transform.root == PlayerObject.transform)
                        return a;
                return null;
            }
        }
        GameObject GetBikeObject(GameObject PlayerObject)
        {
            using (new MethodAnalysis())
            {
                foreach (SkinnedMeshRenderer x in FindObjectsOfType<SkinnedMeshRenderer>())
                    //if (x.gameObject.name == "bike_downhill_LOD0" && x.gameObject.transform.root.name == "Player_Human")
                    if (x.gameObject.name == "bike_downhill_LOD0" && x.gameObject.transform.root == PlayerObject.transform)
                        return x.gameObject;
                return null;
            }
        }
    }
}