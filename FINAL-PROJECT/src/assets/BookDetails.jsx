import {useParams} from 'react-router-dom';

function BookDetails(){
    const {id} = useParams();
    return (
        <div>
            <h2>Book Details</h2>
            <p>Showing details for book ID: {id}</p>
        </div>
    );
}
export default BookDetails;