import React from "react";
import { useState, useEffect } from "react";
import './styles.css';
import Table from "../Table/Table";


function App() {
    const [render, setRender] = useState(false);
    const [items, setItems] = useState([]);
   
    const getItems = async () => {
        const result = [];
        const response = await fetch('http://127.0.0.1:8000/api/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
        })
        let data = await response.json();
        result.push(...data);

        setItems(result);
        
        return setRender(true);
    }

    useEffect(()=>{
        if (items.length === 0) {
            getItems();
            setRender(false);
        }
        if (!render && items.length !== 0) {
            setTimeout(getItems, 2000);
            setRender(false);
        }
    })


    return (
        <div className="wrapper">
            <Table items={items} />
        </div>
    )
}
export default App;