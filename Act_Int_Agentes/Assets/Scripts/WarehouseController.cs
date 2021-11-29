using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
        return wrapper.Items;
    }

    public static string ToJson<T>(T[] array)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper);
    }

    public static string ToJson<T>(T[] array, bool prettyPrint)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper, prettyPrint);
    }

    [System.Serializable]
    private class Wrapper<T>
    {
        public T[] Items;
    }
}

[System.Serializable]
class Agent
{
    public int x;
    public int y;
    public int boxes;
    public int isLoaded;

    override public string ToString()
    {
        return "X: " + x + ", Y: " + y;
    }
}


public class WarehouseController : MonoBehaviour
{
    public int botAmount = 5;
    public int rackAmount = 4;
    public int boxAmount = 20;
    string simulationURL = null;
    private float waitTime = 0.3f;
    private float timer = 0.0f;
    public GameObject robotModel;
    public GameObject rackModel;
    public GameObject boxModel;
    GameObject[] myRobots;
    GameObject[] myRacks;
    GameObject[] myBoxes;

    // Start is called before the first frame update
    void Start()
    {
        myBoxes = new GameObject[boxAmount];
        for (int i = 0; i < boxAmount; i++)
        {
            GameObject box = Instantiate(boxModel, new Vector3(0, 0, 0), Quaternion.identity) as GameObject;
            box.transform.parent = GameObject.Find("BoxCollection").transform;
            myBoxes[i] = box;
        }

        myRacks = new GameObject[rackAmount];
        for (int i = 0; i < rackAmount; i++)
        {
            GameObject rac = Instantiate(rackModel, new Vector3(0, 0, 0), Quaternion.identity) as GameObject;
            rac.transform.parent = GameObject.Find("RackCollection").transform;
            myRacks[i] = rac;
        }

        myRobots = new GameObject[botAmount];
        for (int i = 0; i < botAmount; i++)
        {
            GameObject bot = Instantiate(robotModel, new Vector3(0, 0, 0), Quaternion.identity) as GameObject;
            bot.transform.parent = GameObject.Find("RobotCollection").transform;
            myRobots[i] = bot;
        }

        StartCoroutine(ConnectToMesa());
        
    }

    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/games", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log(www.error);
            }
            else
            {
                simulationURL = www.GetResponseHeader("Location");
                Debug.Log("Connected to simulation through Web API");
                Debug.Log(simulationURL);
            }
        }
    }

    IEnumerator UpdatePositions()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(simulationURL))
        {
            if (simulationURL != null)
            {
                // Request and wait for the desired page.
                yield return www.SendWebRequest();

               // Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");
                Agent[] agents = JsonHelper.FromJson<Agent>(www.downloadHandler.text);
                //Debug.Log(robots[0].ToString());
                //Debug.Log(agents.Length);
                for (int i = 0; i < agents.Length; i++)
                {
                    //Debug.Log(i);
                    if(i < rackAmount)
                    {
                        myRacks[i].transform.position = new Vector3(agents[i].x, 0, agents[i].y);
                        for(int j=0; j < agents[i].boxes; j++){
                            myRacks[i].transform.GetChild(j).gameObject.SetActive(true);
                        }
                    }
                    else if(i >= rackAmount && i < (agents.Length-botAmount))
                    {
                        
                        myBoxes[i - rackAmount].transform.position = new Vector3(agents[i].x, 0, agents[i].y);
                        if (myBoxes[i - rackAmount].transform.position == Vector3.zero)
                        {
                            myBoxes[i - rackAmount].transform.parent = GameObject.Find("UsedBoxesCollection").transform;
                            myBoxes[i - rackAmount].SetActive(false);
                        }
                    }
                    else{
                        Vector3 target = new Vector3(agents[i].x, 0, agents[i].y);
                        myRobots[i - boxAmount - rackAmount].transform.LookAt(new Vector3(agents[i].x, 0, agents[i].y), transform.up);
                        myRobots[i - boxAmount - rackAmount].transform.position = target;
                        //myRobots[i - boxAmount - rackAmount].transform.position = Vector3.MoveTowards(myRobots[i - boxAmount - rackAmount].transform.position, target,1f);

                        if (agents[i].isLoaded == 1){
                            myRobots[i - boxAmount - rackAmount].transform.GetChild(0).gameObject.SetActive(true);
                        }else{
                            myRobots[i - boxAmount - rackAmount].transform.GetChild(0).gameObject.SetActive(false);
                        }

                    }
                    
                }
                
                /*
                myRobots[1].transform.LookAt(new Vector3(robots[1].x, 0, robots[1].y), transform.up);
                myRobots[1].transform.position = new Vector3(robots[1].x, 0, robots[1].y);

                myRobots[2].transform.LookAt(new Vector3(robots[2].x, 0, robots[2].y), transform.up);
                myRobots[2].transform.position = new Vector3(robots[2].x, 0, robots[2].y);

                myRobots[3].transform.LookAt(new Vector3(robots[3].x, 0, robots[3].y), transform.up);
                myRobots[3].transform.position = new Vector3(robots[3].x, 0, robots[3].y);
                */
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer > waitTime)
        {
            StartCoroutine(UpdatePositions());
            timer = timer - waitTime;
        }
    }
}
