import axios from "axios"
import Filepath from "./filepath"
import Filetable from "./filetable"
import { useEffect, useState } from "react"


interface Entity {
    _id: string
    name: string
    type: string
    owner: string
    parent: string
    path: string
}

export type EntityList = Entity[];


async function fetchFiles(): Promise<EntityList> {
    let entities: EntityList = [];

    await axios.get('https://127.0.0.1:8000/api/workspace//', {
        withCredentials: true,
    })
    .then(resp => {
        entities = resp.data['entity_list'];
    })

    return entities;
};


function Content() {
    const [entityList, setEntityList] = useState<EntityList>([]);
    const [path, setPath] = useState<string[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            const data = await fetchFiles();
            const path = data[0].path.split('/').slice(0, -1)
            setEntityList(data);
            setPath(path);
        }

        fetchData();
    }, []);

    return(
        <>
        <Filepath path={path}></Filepath>
        <Filetable entityList={entityList}></Filetable>
        </>
    )
}

export default Content