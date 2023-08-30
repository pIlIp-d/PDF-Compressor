function toFixedIfNecessary(value: string, dp: number) {
    return +parseFloat(value).toFixed(dp);
}

export function humanReadableFileSize(bytes: number) {
    const units = ['Byte', 'kByte', 'MByte', 'GByte', 'TByte'];
    let usedUnit = 0;
    while (bytes / 1000 > 1) {
        usedUnit++;
        bytes /= 1000;
    }
    return toFixedIfNecessary("" + bytes, 1) + " " + units[usedUnit];
}

