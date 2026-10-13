import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
    vus: 50,
    duration: '60s',
};

export default function () {
    const response = http.get('http://gateway:5000/summary');

    check(response, {
        'status is 200': (r) => r.status === 200,
    });

    sleep(0.2);
}