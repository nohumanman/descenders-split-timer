using System.Collections;
using System.Collections.Generic;
using UnityEngine;
public class ObjEnabler : MonoBehaviour
{
    public GameObject obj;
    public KeyCode key = KeyCode.Tab;
    [System.Diagnostics.CodeAnalysis.SuppressMessage("CodeAnalysis", "IDE0051:Unused member", Justification = "Called by Unity DI")]
    void Update()
    {
        if (Input.GetKeyDown(key) || Input.GetKeyDown(KeyCode.CapsLock))
        {
            obj.SetActive(true);
            Cursor.visible = true;
        }
        if (Input.GetKeyUp(key) || Input.GetKeyUp(KeyCode.CapsLock))
        {
            obj.SetActive(false);
            Cursor.visible = false;
        }
    }
}
