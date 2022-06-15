import React from "react";
import './styles.css';

function TableItem({list}){
    
    return (
       <>
             {list.map(el => <tr key={el.id} className="body">
                                <td>{el.id}</td>
                                <td>{el.number}</td>
                                <td>{el.price}</td>
                                <td>{el.date}</td>
                                <td>{el.price_in_rub}</td>
                            </tr>)}
       </>
    )
}

function Table({items}) {
    return (
        <div className="table-wrapper">
            <table className="table">
                <thead>
                    <tr className="head">
                        <th>Id</th>
                        <th>Номер №</th>
                        <th>Стоимость, $</th>
                        <th>Срок доставки</th>
                        <th>Стоимость, ₽</th>
                    </tr>
                </thead>
                <tbody>
                    <TableItem list={items} />
                </tbody>
            </table>
        </div>
    )
}

export default Table;